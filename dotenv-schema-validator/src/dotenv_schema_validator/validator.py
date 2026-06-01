from __future__ import annotations
import json
from pathlib import Path
from typing import Any

import jsonschema
from dotenv import dotenv_values

class ValidationError(Exception):
    pass

def validate_env(env_path: Path, schema_path: Path, strict: bool = True) -> list[dict[str, Any]]:
    env = dotenv_values(env_path)
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in validator.iter_errors(env):
        errors.append({
            "path": list(error.path),
            "message": error.message,
            "line": _find_line(env_path, error.path[0] if error.path else None),
        })
    if strict and errors:
        raise ValidationError(errors)
    return errors

def _find_line(env_path: Path, key: str | None) -> int | None:
    if not key:
        return None
    for i, line in enumerate(env_path.read_text().splitlines(), 1):
        if line.startswith(f"{key}="):
            return i
    return None