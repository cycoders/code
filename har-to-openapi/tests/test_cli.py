import sys
from typer.testing import CliRunner
from har_to_openapi.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Convert HAR files" in result.stdout


def test_cli_invalid_file():
    result = runner.invoke(app, ["nonexistent.har"])
    assert result.exit_code == 1
    assert "Invalid HAR" in result.stdout
