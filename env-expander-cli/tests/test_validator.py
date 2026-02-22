import pytest
from pathlib import Path
from env_expander_cli.validator import validate_env, load_schema


def test_missing_required():
    env = {}
    schema = {"required": ["X"]}
    errors = validate_env(env, schema)
    assert len(errors) == 1
    assert "Missing required variable: X" in errors[0]


def test_pattern_fail():
    env = {"HOST": "invalid@host"}
    schema = {"patterns": {"HOST": r"^[a-z0-9.-]+$"}}
    errors = validate_env(env, schema)
    assert "does not match pattern" in errors[0]


def test_type_int_fail():
    env = {"PORT": "abc"}
    schema = {"types": {"PORT": "int"}}
    errors = validate_env(env, schema)
    assert "not a valid int" in errors[0]


def test_type_bool_ok():
    env = {"FLAG": "true"}
    schema = {"types": {"FLAG": "bool"}}
    errors = validate_env(env, schema)
    assert len(errors) == 0


def test_load_schema(tmp_path: Path):
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text("required: [X]")
    schema = load_schema(schema_path)
    assert schema["required"] == ["X"]