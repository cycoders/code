from datetime import datetime
from typing import List

from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_x509_certificate

from .models import CertificateEntry

def parse_entries(raw_data: List[dict]) -> List[CertificateEntry]:
    entries = []
    for raw in raw_data:
        try:
            entry = CertificateEntry(
                id=raw["ID"],
                logged_at=datetime.fromtimestamp(raw["last_observed"]),
                not_before=datetime.fromtimestamp(raw["not_before"]),
                not_after=datetime.fromtimestamp(raw["not_after"]),
                issuer_name=raw.get("issuer_name", ""),
                common_name=raw.get("name_value", ""),
                cert_link=raw.get("cert_link", ""),
                serial_number=raw.get("Serial", ""),
            )
            entries.append(entry)
        except (KeyError, ValueError, IndexError) as e:
            continue  # Skip malformed
    return entries

def enrich_with_pem(entry: CertificateEntry, pem_text: str) -> None:
    try:
        pem_bytes = pem_text.encode("ascii")
        cert = load_pem_x509_certificate(pem_bytes)
        # SANs
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.OID_SUBJECT_ALTERNATIVE_NAME)
            entry.subject_alt_names = [str(v.value) for v in san_ext.value]
        except x509.ExtensionNotFound:
            entry.subject_alt_names = []
        # Signature algorithm
        try:
            sig_name = cert.signature_algorithm_oid._name.replace("-", " ").title()
            entry.signature_algorithm = sig_name
        except AttributeError:
            pass
        # Public key algorithm
        try:
            algo_name = cert.public_key().__class__.__name__.rpartition("PublicKey")[0]
            entry.public_key_algorithm = algo_name
        except AttributeError:
            pass
    except Exception:
        pass  # Graceful skip