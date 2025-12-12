import pytest
from typing import Any, Dict

from src.openapi_diff_cli.diff_engine import compute_diff


@pytest.fixture
def base_spec() -> Dict[str, Any]:
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
    }


def test_no_changes(base_spec: Dict[str, Any]) -> None:
    result = compute_diff(base_spec, base_spec)
    assert result["summary"]["total_changes"] == 0


def test_add_path(base_spec: Dict[str, Any]) -> None:
    new_spec = base_spec.copy()
    new_spec["paths"]["/test"] = {"get": {}}
    result = compute_diff(base_spec, new_spec)
    changes = result["changes"]
    assert len(changes) >= 1
    path_change = next(c for c in changes if c["location"].startswith("paths./test"))
    assert path_change["impact"] == "non-breaking"
    assert "New API path added" in path_change["description"]


def test_remove_path(base_spec: Dict[str, Any]) -> None:
    old_spec = base_spec.copy()
    old_spec["paths"]["/test"] = {"get": {}}
    result = compute_diff(old_spec, base_spec)
    changes = result["changes"]
    path_change = next(c for c in changes if c["location"] == "paths./test")
    assert path_change["impact"] == "breaking"


def test_add_required_param(base_spec: Dict[str, Any]) -> None:
    old_spec = base_spec.copy()
    old_spec["paths"]["/test"] = {"get": {"parameters": []}}
    new_spec = base_spec.copy()
    new_spec["paths"]["/test"] = {
        "get": {
            "parameters": [
                {"name": "id", "in": "query", "required": True, "schema": {"type": "string"}}
            ]
        }
    }
    result = compute_diff(old_spec, new_spec)
    changes = result["changes"]
    param_change = next(c for c in changes if "parameters[0]" in c["location"])
    assert param_change["impact"] == "breaking"
    assert "Required parameter added" in param_change["description"]


def test_add_optional_param(base_spec: Dict[str, Any]) -> None:
    old_spec = base_spec.copy()
    old_spec["paths"]["/test"] = {"get": {"parameters": []}}
    new_spec = base_spec.copy()
    new_spec["paths"]["/test"] = {
        "get": {
            "parameters": [
                {"name": "filter", "in": "query", "required": False, "schema": {"type": "string"}}
            ]
        }
    }
    result = compute_diff(old_spec, new_spec)
    changes = result["changes"]
    param_change = next(c for c in changes if "parameters[0]" in c["location"])
    assert param_change["impact"] == "non-breaking"


def test_schema_type_change(base_spec: Dict[str, Any]) -> None:
    old_spec = {
        "openapi": "3.0.0",
        "paths": {
            "/test": {
                "get": {
                    "parameters": [
                        {"schema": {"type": "string"}}
                    ]
                }
            }
        },
    }
    new_spec = old_spec.copy()
    new_spec["paths"]["/test"]["get"]["parameters"][0]["schema"]["type"] = "integer"
    result = compute_diff(old_spec, new_spec)
    changes = result["changes"]
    type_change = next(c for c in changes if c["location"].endswith("schema.type"))
    assert type_change["impact"] == "breaking"
    assert "Schema type changed" == type_change["description"]


def test_add_schema(base_spec: Dict[str, Any]) -> None:
    new_spec = base_spec.copy()
    new_spec["components"] = {"schemas": {"NewSchema": {"type": "object"}}}
    result = compute_diff(base_spec, new_spec)
    changes = result["changes"]
    schema_change = next(c for c in changes if c["location"] == "components.schemas.NewSchema")
    assert schema_change["impact"] == "non-breaking"