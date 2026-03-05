import pytest
from unittest.mock import patch, MagicMock
from email.mime.text import MIMEText
from email_header_analyzer.auth_checker import AuthChecker
from email_header_analyzer.parser import parse_email_file_or_stdin

SAMPLE_RAW = b"""DKIM-Signature: v=1; a=rsa-sha256; d=example.net; s=selector;
From: test@example.net

body"""

@pytest.fixture
def sample_msg():
    msg = MIMEText("body")
    msg["From"] = "test@example.net"
    msg["DKIM-Signature"] = "v=1; a=rsa-sha256; d=example.net; s=selector"
    raw = msg.as_bytes()
    return msg, raw

@patch("dkim.verify")
def test_check_dkim(mock_verify, sample_msg):
    mock_verify.return_value = [MagicMock(result="pass", domain="example.net", selector="s1")]
    checker = AuthChecker(sample_msg[0], sample_msg[1])
    dkim = checker.check_dkim()
    assert dkim[0]["result"] == "pass"

@patch("dns.resolver.Resolver")
def test_check_spf_dns_fail(mock_resolver, sample_msg):
    mock_resolver.return_value.resolve.side_effect = Exception("Boom")
    checker = AuthChecker(sample_msg[0], sample_msg[1])
    spf = checker.check_spf()
    assert spf["status"] == "permerror"

@patch("dns.resolver.Resolver")
def test_check_dmarc(mock_resolver, sample_msg):
    m = MagicMock()
    m.resolve.return_value = [MagicMock(to_text=lambda: '"v=DMARC1; p=quarantine;"')]
    mock_resolver.return_value = m
    checker = AuthChecker(sample_msg[0], sample_msg[1])
    dmarc = checker.check_dmarc()
    assert dmarc["status"] == "quarantine"
