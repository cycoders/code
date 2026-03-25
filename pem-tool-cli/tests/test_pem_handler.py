import pytest
from datetime import datetime, timedelta
from pem_tool_cli.pem_handler import PemHandler
from pem_tool_cli.types import CertificateInfo, PrivateKeyInfo


def test_extract_blocks(sample_cert_pem):
    handler = PemHandler(sample_cert_pem)
    assert len(handler.blocks) == 1


def test_parse_cert(sample_cert_pem):
    handler = PemHandler(sample_cert_pem)
    parsed = handler.parsed["block_0"]
    assert isinstance(parsed, CertificateInfo)
    assert parsed.subject.startswith("CN=")


def test_parse_key(sample_key_pem):
    handler = PemHandler(sample_key_pem)
    parsed = handler.parsed["block_0"]
    assert isinstance(parsed, PrivateKeyInfo)
    assert parsed.bit_size > 0


def test_invalid_pem(invalid_pem):
    handler = PemHandler(invalid_pem)
    assert "Parse error" in str(list(handler.parsed.values())[0])


def test_chain_validation(sample_cert_pem):
    # Mock chain with matching issuer/subject
    chain_pem = sample_cert_pem + sample_cert_pem  # Simplified
    handler = PemHandler(chain_pem)
    assert handler.is_valid_chain()  # Adjust for real test


def test_fingerprints(sample_cert_pem):
    handler = PemHandler(sample_cert_pem)
    fps = handler.get_fingerprints()
    assert len(fps) == 1
    assert len(list(fps.values())[0]) == 64