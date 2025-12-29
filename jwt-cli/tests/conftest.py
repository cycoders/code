import pytest
import jwt
import io
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

@pytest.fixture(scope="session")
def rsa_private_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

@pytest.fixture(scope="session")
def rsa_public_pem(rsa_private_pem):
    key = serialization.load_pem_private_key(rsa_private_pem, password=None)
    pub = key.public_key()
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

@pytest.fixture
def hs_secret():
    return b"secret-key-12345"

@pytest.fixture
def now():
    return int(datetime.utcnow().timestamp())

@pytest.fixture
def hs_token(hs_secret, now):
    payload = {"sub": "test", "iat": now, "exp": now + 3600}
    return jwt.encode(payload, hs_secret, "HS256")

@pytest.fixture
def rs_token(rsa_private_pem, now):
    payload = {"sub": "test", "iat": now, "exp": now + 3600}
    return jwt.encode(payload, rsa_private_pem, "RS256")

@pytest.fixture
def expired_hs_token(hs_secret, now):
    payload = {"sub": "test", "exp": now - 100}
    return jwt.encode(payload, hs_secret, "HS256")