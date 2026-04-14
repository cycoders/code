import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from src.cert_transparency_cli.parser import parse_entries, enrich_with_pem, CertificateEntry
from cryptography import x509

sample_raw = [
    {
        "ID": 541884289,
        "not_before": 1640995200,
        "not_after": 1672531200,
        "issuer_name": "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
        "name_value": "example.com",
        "Serial": "01",
        "cert_link": "/541884289.pem",
        "last_observed": 1699123200,
    }
]

@pytest.fixture
def sample_entry():
    return CertificateEntry(
        id=541884289,
        logged_at=datetime(2023, 11, 10, tzinfo=timezone.utc),
        not_before=datetime(2022, 1, 1, tzinfo=timezone.utc),
        not_after=datetime(2023, 1, 1, tzinfo=timezone.utc),
        issuer_name="CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
        common_name="example.com",
        cert_link="/541884289.pem",
        serial_number="01",
    )

def test_parse_entries():
    entries = parse_entries(sample_raw)
    assert len(entries) == 1
    e = entries[0]
    assert e.id == 541884289
    assert e.issuer_name == "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US"
    assert str(e.not_after.year) == "2023"

@patch("cryptography.hazmat.primitives.serialization.load_pem_x509_certificate")
def test_enrich_with_pem(mock_load, sample_entry):
    mock_cert = MagicMock()
    mock_san_ext = MagicMock()
    mock_san_ext.value = MagicMock()
    mock_san_ext.value.get_values_for_type.return_value = [MagicMock(value="dns:example.com")]
    mock_cert.extensions.get_extension_for_oid.return_value = mock_san_ext
    mock_cert.signature_algorithm_oid = MagicMock(_name="sha256-with-rsa-encryption")
    mock_cert.public_key.return_value = MagicMock(__class__=MagicMock(__name__="RSAPublicKey"))
    mock_load.return_value = mock_cert

    pem_text = "fake-pem"
    enrich_with_pem(sample_entry, pem_text)

    assert len(sample_entry.subject_alt_names) == 1
    assert sample_entry.subject_alt_names[0] == "dns:example.com"
    assert "Sha256 With Rsa Encryption" in sample_entry.signature_algorithm
    assert sample_entry.public_key_algorithm == "RSA"

    mock_load.assert_called_once()