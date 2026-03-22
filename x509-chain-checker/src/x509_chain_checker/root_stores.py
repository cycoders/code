from pathlib import Path
from typing import List

import certifi
from x509_chain_checker.cert_utils import parse_pem_bundle, Certificate


def load_trusted_roots(roots_path: Path | None = None) -> List[Certificate]:
    """Load trusted root certs from path or certifi bundle."""
    if roots_path:
        if roots_path.is_dir():
            from x509_chain_checker.cert_utils import load_certs_from_dir
            return load_certs_from_dir(roots_path)
        elif roots_path.is_file():
            with open(roots_path) as f:
                return list(parse_pem_bundle(f.read()))
    # Fallback to certifi
    with open(certifi.where(), "r") as f:
        return list(parse_pem_bundle(f.read()))


def find_anchors(certs: List[Certificate]) -> List[Certificate]:
    """Filter self-signed anchors."""
    anchors = []
    for cert in certs:
        if cert.subject == cert.issuer:
            anchors.append(cert)
    return anchors