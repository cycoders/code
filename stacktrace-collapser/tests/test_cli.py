import pytest
from typer.testing import CliRunner
from stacktrace_collapser.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_empty_input():
    result = runner.invoke(app)
    assert result.exit_code == 1
    assert "No input" in result.stdout


def test_invalid_format():
    result = runner.invoke(app, ["--format", "txt"], input="")
    assert result.exit_code == 1
    assert "Unknown format" in result.stdout
