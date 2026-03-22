import pytest
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from x509_chain_checker.validator import Validator


@pytest.fixture
def now():
    return datetime(2024, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def root_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def root_cert(root_key):
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Root CA")]))
        .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Root CA")]))
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=365))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=2), critical=True)
    )
    return builder.sign(root_key, hashes.SHA256())


@pytest.fixture
def inter_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def inter_cert(root_key, root_cert, inter_key):
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Inter CA")]))
        .issuer_name(root_cert.subject)
        .public_key(inter_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(root_cert.not_valid_before_utc)
        .not_valid_after(root_cert.not_valid_after_utc - timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
    )
    return builder.sign(root_key, hashes.SHA256())


@pytest.fixture
def leaf_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def leaf_cert(inter_key, inter_cert, leaf_key):
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "leaf.example.com")]))
        .issuer_name(inter_cert.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(inter_cert.not_valid_before_utc)
        .not_valid_after(inter_cert.not_valid_after_utc - timedelta(days=1))
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False
        )
    )
    return builder.sign(inter_key, hashes.SHA256())


@pytest.fixture
def good_chain(leaf_cert, inter_cert, root_cert):
    return [leaf_cert, inter_cert, root_cert]


@pytest.fixture
def expired_leaf(inter_key, inter_cert, leaf_key):
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "expired.example.com")]))
        .issuer_name(inter_cert.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=10))
        .not_valid_after(datetime.now(timezone.utc) - timedelta(days=1))
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False
        )
    )
    return builder.sign(inter_key, hashes.SHA256())