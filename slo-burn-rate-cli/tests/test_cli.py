import typer
from typer.testing import CliRunner
from slo_burn_rate_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_invalid_file(tmp_path):
    result = runner.invoke(app, [str(tmp_path / "nonexistent.jsonl")])
    assert result.exit_code == 1
    assert "File not found" in result.stdout
