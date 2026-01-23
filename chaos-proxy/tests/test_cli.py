import sys
from pathlib import Path

import typer
from typer.testing import CliRunner

from chaos_proxy.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Serve a TCP proxy" in result.stdout


def test_serve_minimal() -> None:
    result = runner.invoke(app, ["serve", "example.com:80"])
    assert result.exit_code == 0  # Would run server but mocked


def test_bad_target() -> None:
    result = runner.invoke(app, ["serve", "invalid"])
    assert result.exit_code == 2  # Typer validation
    assert "host:port" in result.stdout
