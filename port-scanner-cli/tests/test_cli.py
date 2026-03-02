import pytest
from typer.testing import CliRunner

from port_scanner_cli.cli import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan targets for open ports" in result.stdout


def test_scan_invalid_target():
    result = runner.invoke(app, ["scan", "invalid"])
    assert result.exit_code == 1
    assert "No valid targets" in result.stdout


def test_scan_invalid_ports():
    result = runner.invoke(app, ["scan", "127.0.0.1", "-p", "invalid"])
    assert result.exit_code == 1
    assert "No valid ports" in result.stdout