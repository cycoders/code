import json
import pytest
from pathlib import Path

from har_to_loadtest.parser import parse_har
from har_to_loadtest.model import HttpRequest


SAMPLE_HAR = "tests/data/sample.har"


@pytest.fixture
def sample_requests():
    return parse_har(SAMPLE_HAR)


def test_parse_valid_har(sample_requests):
    assert len(sample_requests) == 3
    assert all(isinstance(r, HttpRequest) for r in sample_requests)


def test_parse_get_request(sample_requests):
    get_req = sample_requests[0]
    assert get_req.method == "GET"
    assert "authorization" in get_req.headers
    assert get_req.headers["authorization"] == "Bearer abc123def"
    assert get_req.body is None
    assert get_req.json_body is None


def test_parse_json_post(sample_requests):
    post_req = sample_requests[1]
    assert post_req.method == "POST"
    assert post_req.json_body == {"name": "John", "age": 30}
    assert "content-type" in post_req.headers
    assert post_req.headers["content-type"] == "application/json"


def test_parse_nonjson_post(sample_requests):
    nonjson_req = sample_requests[2]
    assert nonjson_req.method == "POST"
    assert nonjson_req.json_body is None
    assert nonjson_req.body == "username=test&password=pass"


def test_empty_entries():
    empty_har = {"log": {"version": "1.2", "entries": []}}
    with pytest.MonkeyPatch.context() as m:
        m.setattr("builtins.open", lambda *args, **kwargs: empty_har)
        reqs = parse_har("fake.har")
    assert len(reqs) == 0


def test_invalid_har_version(monkeypatch):
    invalid_har = {"log": {"version": "9.9"}}
    monkeypatch.setattr("builtins.open", lambda *a, **kw: invalid_har)
    with pytest.raises(ValueError, match="Unsupported HAR version"):
        parse_har("fake.har")
