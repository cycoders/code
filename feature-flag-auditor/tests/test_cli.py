import pytest
from click.testing import CliRunner
from pathlib import Path

from feature_flag_auditor.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scan codebase" in result.stdout


def test_scan_no_config(runner, tmp_path: Path):
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 1
    assert "Config not found" in result.stdout
