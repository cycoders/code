import pytest
from typer.testing import CliRunner
from src.cert_transparency_cli.cli import app

runner = CliRunner()


def test_search_help():
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "Search CT logs" in result.stdout
    assert "--subdomains" in result.stdout
    assert "--fetch-pems" in result.stdout


def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit domain certificates" in result.stdout
    assert "search" in result.stdout