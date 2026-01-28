import pytest
from typing import Any

from openapi_mocker.mock_generator import generate_mock


@pytest.mark.parametrize("schema,expected_type", [
    ({"type": "string"}, str),
    ({"type": "string", "format": "email"}, str),
    ({"type": "integer"}, int),
    ({"type": "number"}, float),
    ({"type": "boolean"}, bool),
    ({"type": "array", "items": {"type": "string"}}, list),
    ({"type": "object", "properties": {"foo": {"type": "string"}}}, dict),
])
def test_generate_mock(schema: dict, expected_type: type):
    data: Any = generate_mock(schema)
    assert isinstance(data, expected_type)


def test_mock_email_format():
    schema = {"type": "string", "format": "email"}
    data = generate_mock(schema)
    assert "@" in data


def test_mock_array_length():
    schema = {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 4}
    data = generate_mock(schema)
    assert len(data) >= 2 and len(data) <= 4
    assert all(isinstance(item, str) for item in data)


def test_mock_nested_object():
    schema = {
        "type": "object",
        "properties": {
            "user": {"type": "object", "properties": {"name": {"type": "string"}}},
        },
    }
    data = generate_mock(schema)
    assert isinstance(data, dict)
    assert isinstance(data.get("user"), dict)
    assert isinstance(data["user"].get("name"), str)


def test_mock_enum():
    schema = {"type": "string", "enum": ["foo", "bar"]}
    data = generate_mock(schema)
    assert data in ["foo", "bar"]