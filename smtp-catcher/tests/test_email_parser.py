import pytest
from smtp_catcher.email_parser import parse_email_parts


@pytest.fixture
def sample_plain_email():
    return b"""From: alice@example.com
To: bob@example.com
Subject: Hello

Plain text body"""

@pytest.fixture
def sample_html_email():
    return b"""From: alice@example.com
To: bob@example.com
Subject: HTML Test
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8

<h1>Hello</h1>"""

@pytest.fixture
def sample_multipart_email():
    return b"""From: alice@example.com
To: bob@example.com
Subject: Multipart
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary=bound

--bound
Content-Type: text/plain

Text part

--bound
Content-Type: text/html

<html>HTML part</html>

--bound--
"""


def test_parse_plain(sample_plain_email):
    parts = parse_email_parts(sample_plain_email)
    assert parts["subject"] == "Hello"
    assert parts["body_text"] == "Plain text body"
    assert parts["body_html"] is None


def test_parse_html(sample_html_email):
    parts = parse_email_parts(sample_html_email)
    assert parts["subject"] == "HTML Test"
    assert parts["body_html"] == "<h1>Hello</h1>"
    assert parts["body_text"] is None


def test_parse_multipart(sample_multipart_email):
    parts = parse_email_parts(sample_multipart_email)
    assert parts["subject"] == "Multipart"
    assert parts["body_text"] == "Text part"
    assert parts["body_html"] == "<html>HTML part</html>"


def test_parse_headers(sample_plain_email):
    parts = parse_email_parts(sample_plain_email)
    assert "From" in parts["headers"]
    assert parts["headers"]["Subject"] == "Hello"