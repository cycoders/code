from typer.testing import CliRunner
from blast_radius_cli.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_diff_runs():
    result = runner.invoke(app, ["diff", "HEAD~1", "HEAD"])
    assert result.exit_code == 0