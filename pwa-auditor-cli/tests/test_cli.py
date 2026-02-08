import json
from typer.testing import CliRunner

from pwa_auditor_cli.main import app

runner = CliRunner()


def test_audit_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit a URL for PWA compliance" in result.stdout


def test_audit_invalid_url():
    result = runner.invoke(app, ["invalid-url"])
    assert result.exit_code == 2  # Typer validation

# Note: Full CLI tests require mocking network, covered in test_auditor
