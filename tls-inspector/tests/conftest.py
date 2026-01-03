# Shared pytest fixtures

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from datetime import datetime, timedelta


@pytest.fixture
def sample_rsa_der():
    """Generate sample RSA cert DER for testing."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "Test.com")])
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("test.com")]),
            critical=False,
        )
    )
    cert = cert_builder.sign(key, hashes.SHA256())
    return cert.public_bytes(serialization.Encoding.DER)


@pytest.fixture
def sample_chain_der(sample_rsa_der):
    """Sample valid chain: leaf + self-signed root."""
    root_der = sample_rsa_der  # reuse as root
    leaf_der = sample_rsa_der  # simplistic
    return [leaf_der, root_der]