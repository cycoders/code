import pytest
from datetime import datetime

from http_cache_analyzer.cache_parser import parse_cache_policy


@pytest.mark.parametrize("headers, expected", [
    (
        {"cache-control": "max-age=3600, public, immutable"},
        {"max_age": 3600},
    ),
    (
        {"cache-control": "no-cache, no-store"},
        {"max_age": None},
    ),
    (
        {"cache-control": "private", "etag": '"abc123"', "expires": "Wed, 21 Oct 2015 07:28:00 GMT"},
        {"max_age": None, "etag": '"abc123"', "expires": datetime(2015, 10, 21, 7, 28, 0)},
    ),
])
def test_parse_cache_policy(headers, expected):
    policy = parse_cache_policy(headers)
    assert policy.max_age == expected["max_age"]
    if "etag" in expected:
        assert policy.etag == expected["etag"]
    if "expires" in expected:
        assert policy.expires == expected["expires"]
