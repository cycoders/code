import pytest
from pathlib import Path

from openapi_auditor_cli.resolver import load_spec, deref_spec, resolve_ref


def test_load_spec(tmp_path: Path):
    spec_path = tmp_path / "test.yaml"
    spec_path.write_text('openapi: 3.1.0')
    spec = load_spec(spec_path)
    assert spec["openapi"] == "3.1.0"


def test_resolve_ref():
    spec = {
        "components": {"schemas": {"User": {"type": "object"}}}
    }
    resolved = resolve_ref(spec, "#/components/schemas/User")
    assert resolved["type"] == "object"


def test_deref_spec():
    spec = {
        "components": {"schemas": {"User": {"type": "string"}}},
        "paths": {"/user": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}}
    }
    resolved = deref_spec(spec)
    assert resolved["paths"]["/user"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["type"] == "string"


def test_broken_ref():
    spec = {"paths": {"/foo": {"$ref": "#/broken"}}}
    resolved = deref_spec(spec)
    assert "$ref_error" in resolved["paths"]["/foo"]
