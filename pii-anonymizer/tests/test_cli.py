import pytest
from typer.testing import CliRunner
from pathlib import Path

from pii_anonymizer.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "detect" in result.stdout


def test_cli_invalid_file(tmp_path: Path):
    result = runner.invoke(app, ["detect", "nonexistent.csv"])
    assert result.exit_code != 0
    assert "not found" in result.stdout.lower()

# Note: Full e2e needs sample files, but unit-focused
