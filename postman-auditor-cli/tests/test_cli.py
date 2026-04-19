import sys
from typer.testing import CliRunner

from postman_auditor_cli.cli import app

runner = CliRunner()


def test_audit_success(tmp_path, demo_collection):  # mock file
    file = tmp_path / "coll.json"
    file.write_text(json.dumps(demo_collection.model_dump()))
    result = runner.invoke(app, ["audit", str(file)])
    assert result.exit_code == 0
    assert "Audit Report" in result.stdout


def test_fail_on_error(tmp_path):
    # Assume demo has errors
    file = tmp_path / "demo.json"
    # write demo
    result = runner.invoke(app, ["audit", str(file), "--fail-level", "error"])
    assert result.exit_code == 1  # since has secrets


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_invalid_json(tmp_path):
    file = tmp_path / "invalid.json"
    file.write_text("{invalid")
    result = runner.invoke(app, ["audit", str(file)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout
