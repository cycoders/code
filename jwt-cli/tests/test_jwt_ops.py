import pytest
from jwt_cli import jwt_ops

# Decode

def test_decode_valid_hs(hs_token):
    header, payload, sig_b64 = jwt_ops.decode_token(hs_token)
    assert header["alg"] == "HS256"
    assert payload["sub"] == "test"
    assert len(sig_b64) > 0

@pytest.mark.rsa
def test_decode_valid_rs(rs_token):
    header, payload, sig_b64 = jwt_ops.decode_token(rs_token)
    assert header["alg"] == "RS256"
    assert payload["sub"] == "test"

# Sign

def test_sign_hs(hs_secret):
    payload = {"foo": "bar", "exp": 9999999999}
    token = jwt_ops.sign_token(payload, "secret", "HS256")
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["foo"] == "bar"

@pytest.mark.rsa
def test_sign_rs(rsa_private_pem):
    payload = {"foo": "bar"}
    token = jwt_ops.sign_token(payload, rsa_private_pem, "RS256")
    decoded = jwt.decode(token, rsa_private_pem, algorithms=["RS256"])
    assert decoded["foo"] == "bar"

# Validate

def test_validate_valid_hs(hs_token, hs_secret):
    valid, errs = jwt_ops.validate_token(hs_token, hs_secret)
    assert valid
    assert not errs

@pytest.mark.rsa
def test_validate_valid_rs(rs_token, rsa_public_pem):
    valid, errs = jwt_ops.validate_token(rs_token, rsa_public_pem)
    assert valid

# Edge cases

def test_validate_expired(expired_hs_token, hs_secret):
    valid, errs = jwt_ops.validate_token(expired_hs_token, hs_secret)
    assert not valid
    assert "expired" in errs[0].lower()

def test_validate_wrong_key(hs_token, rsa_public_pem):
    valid, errs = jwt_ops.validate_token(hs_token, rsa_public_pem)
    assert not valid
    assert "invalid signature" in errs[0].lower()

# Malformed
def test_decode_malformed():
    with pytest.raises(ValueError):
        jwt_ops.decode_token("invalid")

# Issuer/Aud

def test_validate_iss(hs_secret, now):
    payload = {"iss": "wrong", "exp": now + 3600}
    token = jwt.encode(payload, hs_secret, "HS256")
    valid, errs = jwt_ops.validate_token(token, hs_secret, issuer="expected")
    assert not valid
    assert "issuer" in errs[0]