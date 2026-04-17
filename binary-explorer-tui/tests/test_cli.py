import pytest
from typer.testing import CliRunner
from binary_explorer_tui.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_invalid_path(mocker):
    mocker.patch("binary_explorer_tui.analyzer.BinaryAnalyzer", side_effect=ValueError("fail"))
    result = runner.invoke(app, ["info", "/fake"])
    assert result.exit_code == 1
    assert "Cannot parse" in result.stdout
