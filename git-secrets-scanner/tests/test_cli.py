import pytest
from typer.testing import CliRunner
from git_secrets_scanner.cli import app

runner = CliRunner()


def test_scan_clean_exit_zero(clean_temp_dir):
    result = runner.invoke(app, ["scan", str(clean_temp_dir)])
    assert result.exit_code == 0
    assert "No secrets" in result.stdout


def test_patterns_command(temp_repo):
    result = runner.invoke(app, ["patterns"])
    assert result.exit_code == 0
    assert "aws_access_key_id" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout