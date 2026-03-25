import pytest
from typer.testing import CliRunner
from pem_tool_cli.cli import app

runner = CliRunner()


def test_inspect_help():
    result = runner.invoke(app, ["inspect", "--help"])
    assert result.exit_code == 0
    assert "Inspect PEM blocks" in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0

# Note: Full CLI tests require files; mocked here


def test_validate_invalid(tmp_path):
    invalid_file = tmp_path / "invalid.pem"
    invalid_file.write_text("invalid")
    result = runner.invoke(app, ["validate", str(invalid_file)])
    assert result.exit_code == 0  # Graceful


def test_fingerprint_json(tmp_path, sample_cert_pem):
    f = tmp_path / "cert.pem"
    f.write_text(sample_cert_pem)
    result = runner.invoke(app, ["fingerprint", str(f), "--json"])
    assert result.exit_code == 0
    assert '"sha256_fingerprint"' in result.stdout