import pytest
from typer.testing import CliRunner
from git_blame_tui.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_no_file():
    result = runner.invoke(app)
    assert result.exit_code != 0
    assert "Error: Missing argument" in result.stdout


def test_cli_file_not_found(tmp_path):
    result = runner.invoke(app, [str(tmp_path / "nonexistent")])
    assert result.exit_code != 0
