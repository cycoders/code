import pytest
from email.mime.text import MIMEText
from email_header_analyzer.parser import (
    parse_email_file_or_stdin,
    extract_received,
    extract_auth_results,
    get_envelope_info,
)

RAW_EMAIL = b"""Return-Path: <bounce@example.com>
From: user@example.com
Received: from mail.ex.com ([203.0.113.1]) by relay.net;
Subject: Test

Body text"""

RAW_NO_RECEIVED = b"""From: test@ex.com

Hi"""

@pytest.mark.parametrize(
    "raw,exp_domain",
    [(RAW_EMAIL, "example.com"), (RAW_NO_RECEIVED, "ex.com")],
)
def test_get_envelope_info(raw):
    from email.parser import BytesParser
    from email.policy import default
    msg = BytesParser(policy=default).parsebytes(raw)
    info = get_envelope_info(msg)
    assert "example.com" in info["from_domain"]


def test_extract_received():
    msg = BytesParser(policy=default).parsebytes(RAW_EMAIL)
    chain = extract_received(msg)
    assert len(chain) == 1
    assert chain[0]["ip"] == "203.0.113.1"
    assert "mail.ex.com" in chain[0]["helo"]


def test_extract_auth_results():
    raw = b"""Authentication-Results: mx.google.com; spf=pass smtp.mailfrom=example.com"""
    msg = BytesParser(policy=default).parsebytes(raw)
    results = extract_auth_results(msg)
    assert len(results) == 1
    assert results[0]["spf"] == "pass"
