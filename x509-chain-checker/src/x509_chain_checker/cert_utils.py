from pathlib import Path
import re
from typing import List, Iterator

from cryptography.hazmat.primitives.serialization import load_pem_x509_certificate

from cryptography.x509 import Certificate
from cryptography.hazmat.backends import default_backend


def load_cert(path: Path) -> Certificate:
    """Load single cert from PEM/DER file."""
    with open(path, "rb") as f:
        data = f.read()
    if path.suffix == ".der":
        from cryptography.hazmat.primitives.serialization import load_der_x509_certificate
        return load_der_x509_certificate(data, default_backend())
    return load_pem_x509_certificate(data, default_backend())


def load_certs_from_dir(dir_path: Path) -> List[Certificate]:
    """Load all PEM/DER certs from directory."""
    certs = []
    for p in dir_path.rglob("*.pem"):
        try:
            certs.append(load_cert(p))
        except Exception:
            pass  # Graceful
    for p in dir_path.rglob("*.der"):
        try:
            certs.append(load_cert(p))
        except Exception:
            pass
    return certs


def parse_pem_bundle(pem_str: str) -> Iterator[Certificate]:
    """Yield certs from PEM bundle."""
    parts = re.split(b"-----BEGIN CERTIFICATE-----", pem_str.encode(), flags=re.MULTILINE)
    for part in parts[1:]:
        match = re.match(rb"([^-]+?-----END CERTIFICATE-----)", part, re.DOTALL)
        if match:
            pem_bytes = b"-----BEGIN CERTIFICATE-----" + match.group(0)
            try:
                yield load_pem_x509_certificate(pem_bytes, default_backend())
            except Exception:
                pass


def cert_to_pem(cert: Certificate) -> str:
    return cert.public_bytes(encoding=serialization.Encoding.PEM).decode()