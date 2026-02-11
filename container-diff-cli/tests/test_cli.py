import typer
from typer.testing import CliRunner
from container_diff_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Diff two images" in result.stdout


def test_cli_diff(mock_client):
    result = runner.invoke(app, ["img1", "img2"])
    assert result.exit_code == 0
    assert "Container Diff" in result.stdout
