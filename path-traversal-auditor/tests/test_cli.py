from typer.testing import CliRunner
from path_traversal_auditor.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_scan_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["scan", "."])
    assert "Scanning" in result.output