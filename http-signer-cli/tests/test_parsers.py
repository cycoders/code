import pytest
from http_signer_cli.parsers import parse_curl


def test_parse_curl_get():
    curl = "curl https://example.com"
    parsed = parse_curl(curl)
    assert parsed["method"] == "GET"
    assert parsed["url"] == "https://example.com"
    assert parsed["headers"] == {}
    assert parsed["body"] == ""


def test_parse_curl_post_header_data():
    curl = "curl -X POST -H 'Content-Type: app/json' -d 'body' https://ex.com/api"
    parsed = parse_curl(curl)
    assert parsed["method"] == "POST"
    assert parsed["url"] == "https://ex.com/api"
    assert parsed["headers"] == {"Content-Type": "app/json"}
    assert parsed["body"] == "body"


def test_parse_curl_no_url():
    with pytest.raises(ValueError, match="No URL"):
        parse_curl("curl -X POST")


def test_parse_curl_invalid():
    with pytest.raises(ValueError, match="Invalid curl"):
        parse_curl("notcurl")
