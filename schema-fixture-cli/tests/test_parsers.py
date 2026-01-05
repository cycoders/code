import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from schema_fixture_cli.parsers import get_schema_dict, is_openapi


@pytest.fixture
def simple_schema_path(tmp_path: Path):
    schema_path = tmp_path / "simple.json"
    schema_path.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }
        )
    )
    return schema_path


class TestParsers:
    def test_load_json_schema(self, simple_schema_path: Path):
        schema = get_schema_dict(simple_schema_path, None, "", None)
        assert schema["properties"]["name"]["type"] == "string"

    def test_is_openapi(self):
        assert is_openapi({"openapi": "3.0.0"})
        assert is_openapi({"swagger": "2.0"})
        assert not is_openapi({"type": "object"})


# Integration-like
class TestPydanticParser:
    # Requires writing py file
    def test_pydantic_example(self, tmp_path: Path):
        py_path = tmp_path / "model.py"
        py_path.write_text("""
from pydantic import BaseModel
class Test(BaseModel):
    name: str
""")
        schema = get_schema_dict(None, py_path, "Test", None)
        assert "name" in schema["properties"]
