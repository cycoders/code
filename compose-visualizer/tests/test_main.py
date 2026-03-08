import pytest
from typer.testing import CliRunner
from compose_visualizer.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Visualize" in result.stdout
    assert "audit" in result.stdout


def test_cli_visualize_missing(mocker):
    mocker.patch("pathlib.Path.exists", return_value=False)
    result = runner.invoke(app, ["visualize", "missing.yml"])
    assert result.exit_code == 1
    assert "not found" in result.stdout