import pytest
from typer.testing import CliRunner

from http3_tester_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Benchmark HTTP/3" in result.stdout


def test_cli_invalid_url():
    result = runner.invoke(app, ["http://invalid"])
    assert result.exit_code == 1
    assert "Only HTTPS" in result.stdout
