import json
from typer.testing import CliRunner
from upgrade_dryrun.cli import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan directory for workspaces" in result.stdout


def test_run_invalid_ecosystem():
    result = runner.invoke(app, ["run", ".", "invalid"])
    assert result.exit_code == 1
    assert "Unknown ecosystem" in result.stdout
