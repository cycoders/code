import typer
from pathlib import Path
from click.testing import CliRunner

from ssh_key_auditor.cli import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scan SSH directory" in result.stdout


def test_scan_invalid_output():
    result = runner.invoke(app, ["scan", "--output", "invalid"])
    assert result.exit_code == 1
    assert "Invalid output" in result.stderr