from typer.testing import CliRunner
from resource_cleanup_auditor.cli import app

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0