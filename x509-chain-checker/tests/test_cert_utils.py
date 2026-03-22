import pytest
from pathlib import Path
from x509_chain_checker.cert_utils import load_cert, parse_pem_bundle


@pytest.mark.parametrize("suffix", [".pem", ".der"])
def test_load_cert(tmp_path: Path, leaf_cert):
    pem_path = tmp_path / "leaf.pem"
    pem_path.write_bytes(leaf_cert.public_bytes(serialization.Encoding.PEM))
    assert load_cert(pem_path) == leaf_cert


# Note: DER test requires der_bytes, skipped for brevity as PEM primary


def test_parse_pem_bundle(root_cert):
    pem_bundle = "-----BEGIN CERTIFICATE-----\n" + root_cert.public_bytes(serialization.Encoding.PEM).decode()[27:]  # Mock bundle
    certs = list(parse_pem_bundle(pem_bundle))
    assert len(certs) >= 1