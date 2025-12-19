import pytest
from json_surgeon_cli.schema_validator import validate_json


def test_valid_schema():
    instance = {"a": 1}
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}}
    valid, errors = validate_json(instance, schema)
    assert valid
    assert not errors


def test_invalid_schema():
    instance = {"a": "not-int"}
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}}
    valid, errors = validate_json(instance, schema)
    assert not valid
    assert len(errors) > 0
    assert "integer" in errors[0]


def test_nested_invalid():
    instance = {"list": [{"b": "str"}]}
    schema = {"properties": {"list": {"items": {"properties": {"b": {"type": "number"}}}}}
    valid, _ = validate_json(instance, schema)
    assert not valid
