from har_to_openapi.utils import safe_json_load


def test_safe_json_load_valid():
    assert safe_json_load('{"key": "value"}') == {"key": "value"}


def test_safe_json_load_invalid():
    assert safe_json_load("invalid json") is None
