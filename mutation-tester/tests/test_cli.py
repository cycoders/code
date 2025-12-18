import pytest
from typer.testing import CliRunner
from mutation_tester.cli import cli_app

runner = CliRunner()


def test_help():
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "Run mutation testing" in result.stdout


def test_invalid_dir():
    result = runner.invoke(cli_app, ["nonexistent"])
    assert result.exit_code == 1
    assert "No mutants found" in result.stdout