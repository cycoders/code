import pytest
from git_secrets_scanner.detectors import detect_in_text, PATTERNS


@pytest.fixture
def default_params():
    return PATTERNS, 3.5, 20, []


def test_detect_aws_key(default_params):
    patterns, thresh, minlen, allow = default_params
    text = "My AWS_KEY=AKIA1234567890123456 is here"
    hits = detect_in_text(text, patterns, thresh, minlen, allow)
    assert len(hits) == 1
    assert hits[0].detector_id == "aws_access_key_id"
    assert "AKIA" in hits[0].snippet


def test_entropy_detection(default_params):
    patterns, thresh, minlen, allow = default_params
    high_ent = "SG.dGVzdF9zZWNyZXRfdG9rZW4_1234567890abcdef=="
    text = f"Line1\n{high_ent}\nLine3"
    hits = detect_in_text(text, patterns, thresh, minlen, allow)
    assert any(h.detector_id == "high_entropy" for h in hits)


def test_allowlist_skips(default_params):
    patterns, thresh, minlen, allow = default_params
    text = "Ignore this AKIA1234567890123456"
    hits = detect_in_text(text, patterns, thresh, minlen, ["AKIA1"])
    assert len(hits) == 0