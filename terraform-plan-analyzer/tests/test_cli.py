from typer.testing import CliRunner
import pytest
from terraform_plan_analyzer.cli import app

runner = CliRunner()


def test_cli_summary(sample_plan: Path):
    result = runner.invoke(app, ["summary", str(sample_plan)])
    assert result.exit_code == 0
    assert "CREATE" in result.stdout
    assert "aws_instance" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_cli_invalid_file():
    result = runner.invoke(app, ["summary", "nonexistent.json"])
    assert result.exit_code != 0
    assert "exists" in result.stdout.lower()