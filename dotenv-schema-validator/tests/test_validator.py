import pytest
from pathlib import Path
from dotenv_schema_validator.validator import validate_env, ValidationError

def test_valid_env(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("DATABASE_URL=postgres://localhost/db\nPORT=5432\n")
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","properties":{"DATABASE_URL":{"type":"string"},"PORT":{"type":"integer"}},"required":["DATABASE_URL"]}')
    assert validate_env(env, schema) == []

def test_missing_required(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("PORT=8080\n")
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","required":["DATABASE_URL"]}')
    errors = validate_env(env, schema, strict=False)
    assert len(errors) == 1

def test_type_mismatch(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("PORT=notanumber\n")
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","properties":{"PORT":{"type":"integer"}}}')
    errors = validate_env(env, schema, strict=False)
    assert "type" in errors[0]["message"].lower()