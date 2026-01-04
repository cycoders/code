import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from json_schema_inferrer.cli import app

runner = CliRunner()


def test_infer_help():
    result = runner.invoke(app, ["infer", "--help"])
    assert result.exit_code == 0
    assert "Infer schema from JSON samples" in result.stdout


def test_validate_help():
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0


@pytest.fixture
def simple_json(tmp_path: Path):
    p = tmp_path / "simple.json"
    p.write_text(
        json.dumps({"id": 123, "name": "test", "flag": True}),
        encoding="utf-8",
    )
    return p


def test_infer_simple(tmp_path: Path, simple_json: Path):
    out = tmp_path / "schema.json"
    result = runner.invoke(
        app, ["infer", str(simple_json), "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    schema = json.loads(out.read_text())
    assert schema["type"] == "object"
    assert "required" in schema


def test_validate_good(tmp_path: Path, simple_json: Path):
    schema_path = tmp_path / "schema.json"
    runner.invoke(app, ["infer", str(simple_json), "-o", str(schema_path)])
    result = runner.invoke(app, ["validate", str(schema_path), str(simple_json)])
    assert result.exit_code == 0
    assert "✓" in result.stdout


def test_invalid_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("invalid")
    result = runner.invoke(app, ["infer", str(bad)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stderr
