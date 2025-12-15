import sys
from typer.testing import CliRunner
from snippet_vault.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_list_help():
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
