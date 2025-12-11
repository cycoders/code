'''Tests for parser.''' 

import json
import pytest
from curl_to_python.parser import parse_curl
from curl_to_python.models import CurlParsed


@pytest.mark.parametrize(
    "curl_command, expected",
    [
        (
            "curl https://example.com",
            CurlParsed(method="GET", url="https://example.com"),
        ),
        (
            "curl -X POST https://api.example.com",
            CurlParsed(method="POST", url="https://api.example.com"),
        ),
        (
            'curl -H "Authorization: Bearer token" https://api.com',
            CurlParsed(
                url="https://api.com",
                headers={"Authorization": "Bearer token"},
            ),
        ),
        (
            'curl -u user:pass https://api.com',
            CurlParsed(url="https://api.com", auth_user="user", auth_pass="pass"),
        ),
        (
            'curl -d "{\"key\":\"value\"}" https://api.com -H "Content-Type: application/json"',
            CurlParsed(
                url="https://api.com",
                headers={"Content-Type": "application/json"},
                json_data={"key": "value"},
            ),
        ),
        (
            'curl -X POST -F "file=@/path/to/file.txt" https://upload.com',
            CurlParsed(
                method="POST",
                url="https://upload.com",
                files={"file": "/path/to/file.txt"},
            ),
        ),
        (
            'curl -G -d "q=hello+world" https://search.com',
            CurlParsed(
                url="https://search.com",
                is_get=True,
                params={"q": "hello world"},
            ),
        ),
    ],
)
def test_parse_curl(curl_command, expected):
    """Test parsing common cases."""
    result = parse_curl(curl_command)
    # Compare non-default fields
    assert result.method == expected.method
    assert result.url == expected.url
    assert result.headers == expected.headers
    assert result.auth_user == expected.auth_user
    assert result.auth_pass == expected.auth_pass
    assert result.json_data == expected.json_data
    assert result.files == expected.files
    assert result.params == expected.params


def test_parse_invalid():
    """Test invalid inputs."""
    with pytest.raises(ValueError, match="Must start with 'curl'"):
        parse_curl("invalid")
    with pytest.raises(ValueError, match="No URL found"):
        parse_curl("curl -X POST")


def test_warnings(capfd):
    """Test unsupported flags warn."""
    parse_curl("curl https://ex.com --insecure -cacert foo")
    captured = capfd.readouterr()
    assert "Unsupported flag" in captured.err
