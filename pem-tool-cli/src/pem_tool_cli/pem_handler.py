import base64
import re
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa
from cryptography.exceptions import InvalidSignature

from rich import print as rprint
from .types import CertificateInfo, PrivateKeyInfo, CsrInfo, PemParseResult


class PemHandler:
    def __init__(self, pem_content: str, password: Optional[bytes] = None):
        self.pem_content = pem_content
        self.password = password
        self.blocks: List[Tuple[str, str]] = self._extract_blocks()
        self.parsed: PemParseResult = self._parse_blocks()

    def _extract_blocks(self) -> List[Tuple[str, str]]:
        """Extract PEM blocks using regex."""
        pattern = r'-----BEGIN ([A-Z0-9 \-]+?)-----\n([A-Za-z0-9+/=\n]+?)\n-----END \1-----'
        matches = re.finditer(pattern, self.pem_content, re.DOTALL)
        return [(match.group(1).strip(), match.group(2).strip()) for match in matches]

    def _parse_block(self, block_type: str, body: str) -> Any:
        pem_full = f"-----BEGIN {block_type}-----\n{body}\n-----END {block_type}-----"
        data = pem_full.encode()
        try:
            if 'CERTIFICATE' in block_type.upper():
                cert = x509.load_pem_x509_certificate(data)
                san = [name.value for name in cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value.get_values_for_type(x509.NameAttribute)]
                return CertificateInfo(
                    subject=cert.subject.rfc4514_string(),
                    issuer=cert.issuer.rfc4514_string(),
                    not_valid_before=cert.not_valid_before_utc,
                    not_valid_after=cert.not_valid_after_utc,
                    serial_number=str(cert.serial_number),
                    key_algorithm=cert.public_key()._key_type(),  # Simplified
                    key_size=getattr(cert.public_key(), 'key_size', None),
                    subject_alt_names=san,
                    sha256_fingerprint=cert.fingerprint(hashes.SHA256()).hex().upper(),
                    version=f"v{cert.version.value}",
                )
            elif 'PRIVATE KEY' in block_type.upper() or 'RSA PRIVATE' in block_type.upper():
                key = serialization.load_pem_private_key(data, self.password)
                pub_bytes = key.public_key().public_bytes(
                    serialization.Encoding.DER,
                    serialization.PublicFormat.SubjectPublicKeyInfo
                )
                fp = hashes.Hash(hashes.SHA256()).update(pub_bytes).finalize().hex().upper()
                size = key.key_size if hasattr(key, 'key_size') else 0
                algo = type(key).__name__.replace('PrivateKey', '')
                modulus = key.public_key().public_numbers().n if isinstance(key, rsa.RSAPrivateKey) else None
                return PrivateKeyInfo(
                    algorithm=algo,
                    bit_size=size,
                    sha256_fingerprint=fp,
                    public_modulus=f"0x{modulus:x}" if modulus else None,
                )
            elif 'CERTIFICATE REQUEST' in block_type.upper():
                csr = x509.load_pem_x509_csr(data)
                pub_key = csr.public_key()
                size = pub_key.key_size if hasattr(pub_key, 'key_size') else 0
                fp = hashes.Hash(hashes.SHA256()).update(
                    pub_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
                ).finalize().hex().upper()
                return CsrInfo(
                    subject=csr.subject.rfc4514_string(),
                    public_key_algorithm=type(pub_key).__name__,
                    public_key_size=size,
                    sha256_fingerprint=fp,
                )
            else:
                return f"Unsupported block type: {block_type}"
        except Exception as e:
            return f"Parse error: {str(e)}"

    def _parse_blocks(self) -> PemParseResult:
        return {f"block_{i}": self._parse_block(typ, body) for i, (typ, body) in enumerate(self.blocks)}

    def is_valid_chain(self) -> bool:
        certs = [b for b in self.parsed.values() if isinstance(b, CertificateInfo)]
        if not certs:
            return False
        # Simple chain: leaf issuer matches intermediate subject, etc.
        for i in range(1, len(certs)):
            if certs[i-1].issuer != certs[i].subject:
                return False
        # Check expirations
        now = datetime.utcnow()
        return all(c.not_valid_after > now > c.not_valid_before for c in certs)

    def get_fingerprints(self) -> Dict[str, str]:
        fps = {}
        for k, v in self.parsed.items():
            if hasattr(v, 'sha256_fingerprint'):
                fps[k] = v.sha256_fingerprint
        return fps