import hashlib
import pytest
from freezegun import freeze_time
from http_signer_cli.signers.aws4 import sign_aws4, _prep_signing_key
from http_signer_cli.signers.oauth1 import sign_oauth1


@freeze_time("2015-12-21 20:49:57")
def test_aws4_example():
    url = "https://example.amazonaws.com"
    headers = {}
    body = b""
    signed = sign_aws4(
        "GET",
        url,
        headers,
        body,
        "AKIDEXAMPLE",
        "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "us-east-1",
        "iam",
    )
    # From AWS docs example (simplified)
    assert signed["host"] == "example.amazonaws.com"
    assert "AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/" in signed["Authorization"]
    assert signed["x-amz-content-sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_aws4_post():
    signed = sign_aws4(
        "POST",
        "https://ex.com",
        {},
        b'{"test":1}',
        "ak",
        "sk",
        "reg",
        "svc",
    )
    assert "x-amz-content-sha256" in signed

@freeze_time("2023-01-01 00:00:01")
def test_oauth1_example():
    url = "https://api.example.com/1.0"
    headers = {}
    body = b""
    signed = sign_oauth1(
        "GET",
        url,
        headers,
        body,
        consumer_key="xvz1evFS4wEEPTGEFPHBog",
        consumer_secret="L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg",
        access_token="370773112-Gm4TDdv99SQ74XQT7B8G5rRjcLnggaEYsA2OKTW8",
        token_secret="LswwdoUaIvSGuR0fmoAuqUxkjtzEFPc0eloeG8G8",
    )
    auth = signed["Authorization"]
    assert auth.startswith("OAuth oauth_consumer_key=\"xvz1evFS4wEEPTGEFPHBog\"")
    assert "oauth_nonce=" in auth
    assert "oauth_timestamp=\"1672531201\"" in auth
    assert "oauth_signature=" in auth


def test_prep_signing_key():
    dt = datetime(2015, 12, 21, tzinfo=timezone.utc)
    key = _prep_signing_key("secret", dt, "us-east-1", "iam")
    # Known hash from AWS docs
    assert key.hex() == "f4780e2d9f65fa895f9c67b32ce1baf0b0d8a43505a000a1a9e090d414db404d"  # Truncated example
