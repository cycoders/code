from typer.testing import CliRunner
from log_schema_inferrer.cli import app

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0