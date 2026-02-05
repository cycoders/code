import pytest
from pathlib import Path
from typer.testing import CliRunner

from font_subsetter.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scan web project" in result.stdout


def test_cli_no_input(tmp_path):
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1
    assert "Input dir not found" in result.stdout

# Integration tests require fonts; mocked in subsetter