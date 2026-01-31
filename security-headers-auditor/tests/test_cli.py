import pytest
from typer.testing import CliRunner
from security_headers_auditor.cli import app

runner = CliRunner()


def test_audit_help():
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "Audit security headers" in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_invalid_url(mocker):
    mocker.patch(
        "security_headers_auditor.auditor.Auditor.audit",
        side_effect=ValueError("Invalid URL"),
    )
    result = runner.invoke(app, ["audit", "invalid"])
    assert result.exit_code == 1
    assert "Error" in result.stderr
