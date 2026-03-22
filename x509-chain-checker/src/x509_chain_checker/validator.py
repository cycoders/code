from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from enum import Enum

import x509
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

from x509_chain_checker.models import Status, Issue, CertValidation, ChainReport
from x509_chain_checker.cert_utils import Certificate


PURPOSE_EKUS = {
    "server": [x509.oid.ExtendedKeyUsageOID.SERVER_AUTH],
    "client": [x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH],
    "ca": [x509.oid.KeyIdLookup.OID_BASIC_CONSTRAINTS_CA],
    "any": [],
}


class Validator:
    def __init__(self, purpose: str = "server"):
        self.purpose = purpose
        self.eku_oids = PURPOSE_EKUS.get(purpose, [])

    def build_chain(
        self, leaf: Certificate, pool: List[Certificate]
    ) -> List[Certificate]:
        chain = [leaf]
        current = leaf
        seen = {leaf}
        while True:
            issuer = self._find_issuer(current, pool)
            if not issuer or issuer in seen:
                break
            chain.append(issuer)
            current = issuer
            seen.add(issuer)
        return chain

    def _find_issuer(self, cert: Certificate, pool: List[Certificate]) -> Optional[Certificate]:
        for candidate in pool:
            if candidate.subject == cert.issuer:
                return candidate
        return None

    def validate(self, chain: List[Certificate], roots: List[Certificate]) -> ChainReport:
        validated = []
        issues = []
        for i, cert in enumerate(chain):
            parent = chain[i + 1] if i + 1 < len(chain) else None
            cert_val, cert_issues = self._validate_cert(cert, parent, roots, i)
            validated.append(cert_val)
            issues.extend(cert_issues)
        overall = self._overall_status(validated)
        return ChainReport(
            chain=validated,
            overall_status=overall,
            summary=f"{len([v for v in validated if v.status != Status.VALID])} issues found",
            num_issues=len(issues),
        )

    def _validate_cert(
        self, cert: Certificate, parent: Optional[Certificate], roots: List[Certificate], depth: int
    ) -> Tuple[CertValidation, List[Issue]]:
        issues = []
        now = datetime.now(timezone.utc)
        # Dates
        if cert.not_valid_after < now:
            issues.append(Issue.EXPIRED)
        if cert.not_valid_before > now:
            issues.append(Issue.NOT_YET_VALID)
        # Signature
        if parent and not self._verify_signature(cert, parent):
            issues.append(Issue.SIGNATURE_INVALID)
        # Self-signed
        if cert.subject == cert.issuer and cert not in roots:
            issues.append(Issue.SELF_SIGNED_NOT_ROOT)
        # Purpose
        try:
            ku = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
            if self.purpose != "any" and not any(ku.value.key_purposes):
                issues.append(Issue.WRONG_PURPOSE)
        except x509.ExtensionNotFound:
            pass
        try:
            eku = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.EXTENDED_KEY_USAGE)
            if self.eku_oids and not any(oid in self.eku_oids for oid in eku.value._key_purpose_oids):
                issues.append(Issue.WRONG_PURPOSE)
        except x509.ExtensionNotFound:
            pass
        # Basic constraints path len
        try:
            bc = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.BASIC_CONSTRAINTS)
            if bc.value.ca and bc.value.path_length_constraint is not None and depth > bc.value.path_length_constraint:
                issues.append(Issue.PATH_LEN_EXCEEDED)
        except x509.ExtensionNotFound:
            pass
        # Weak key (simple check)
        if cert.public_key().key_size < 2048:
            issues.append(Issue.WEAK_KEY)
        status = Status.VALID if not issues else Status.INVALID if any(iss in (Issue.SIGNATURE_INVALID, Issue.UNTRUSTED_ISSUER) for iss in issues) else Status.WARNING
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        cn_str = cn[0].value if cn else "Unknown"
        return (
            CertValidation(
                subject_cn=cn_str,
                issuer_cn=parent.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value if parent else "",
                serial=str(cert.serial_number),
                not_before=cert.not_valid_before_utc,
                not_after=cert.not_valid_after_utc,
                status=status,
                issues=issues,
                fingerprint_sha256=cert.fingerprint(hashes.SHA256()).hex(),
            ),
            issues,
        )

    def _verify_signature(self, child: Certificate, parent: Certificate) -> bool:
        try:
            child.public_key().verify(
                child.signature,
                child.tbs_certificate_bytes,
                child.signature_algorithm_parameters,
                child.signature_hash_algorithm,
            )
            return True
        except InvalidSignature:
            return False

    def _overall_status(self, validated: List[CertValidation]) -> Status:
        if all(v.status == Status.VALID for v in validated):
            return Status.VALID
        if any(v.status == Status.INVALID for v in validated):
            return Status.INVALID
        return Status.WARNING