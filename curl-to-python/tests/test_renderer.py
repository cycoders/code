'''Tests for renderer.''' 

import pytest
from curl_to_python.models import CurlParsed
from curl_to_python.renderer import dict_to_literal, parsed_to_code


@pytest.fixture
def simple_parsed():
    """Simple parsed fixture."""
    return CurlParsed(
        method="POST",
        url="https://api.example.com",
        headers={"Content-Type": "application/json"},
        json_data={"key": "value"},
    )


def test_dict_to_literal():
    """Test dict literal formatter."""
    d = {"Accept": "*/*", "User-Agent": "curl/7.0"}
    expected = '{\n    "Accept": "*/*",\n    "User-Agent": "curl/7.0"\n}'
    assert dict_to_literal(d) == expected
    assert dict_to_literal({}) == "{}"


def test_parsed_to_code_requests(simple_parsed):
    """Test requests code gen."""
    code = parsed_to_code(simple_parsed)
    assert "import requests" in code
    assert 'requests.post(' in code
    assert '"https://api.example.com"' in code
    assert '"Content-Type": "application/json"' in code
    assert '"key": "value"' in code
    assert "raise_for_status()" in code


def test_parsed_to_code_httpx_async():
    """Test httpx async."""
    parsed = CurlParsed(url="https://ex.com", auth_user="u", auth_pass="p")
    code = parsed_to_code(parsed, httpx=True, async_=True)
    assert "import httpx" in code
    assert "async with httpx.AsyncClient()" in code
    assert "await client.get(" in code
    assert "auth=(\n    'u', 'p'" in code


def test_files_form():
    """Test files and form data."""
    parsed = CurlParsed(
        url="https://upload.com",
        files={"doc": "file.pdf"},
        form_data={"title": "test"},
    )
    code = parsed_to_code(parsed)
    assert "files={" in code
    assert "'doc': ('file.pdf', open('file.pdf', 'rb'))" in code
    assert "data={'title': 'test'}" in code
