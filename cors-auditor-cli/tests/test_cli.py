import typer
from typer.testing import CliRunner

from cors_auditor_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit CORS configuration" in result.stdout


def test_cli_invalid_url():
    result = runner.invoke(app, ["test", "invalid-url"])
    assert result.exit_code == 1
    assert "URL must include scheme" in result.stdout