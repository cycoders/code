import hmac
import hashlib
from webhook_inspector.handlers import SignatureVerifier


def test_github_verify():
    secret = b"testsecret"
    payload = b'{"event": "ping"}'
    sig = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    assert SignatureVerifier.verify_github(payload, sig, "testsecret")


def test_stripe_verify():
    # Mock timestamp
    import time
    original_time = time.time
    time.time = lambda: 1699999999.0
    try:
        payload = b'{"type": "event"}'
        sig = "t=1699999999,v1=" + hmac.new(
            b"whsec_test", f"t=1699999999.{payload.decode()}".encode(), hashlib.sha256
        ).hexdigest()
        assert SignatureVerifier.verify_stripe(payload, sig, "whsec_test")
    finally:
        time.time = original_time


def test_slack_verify():
    secret = b"testsecret"
    payload = b'{"type": "url_verification"}'
    sig = "v0=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    assert SignatureVerifier.verify_slack(payload, sig, "testsecret")
