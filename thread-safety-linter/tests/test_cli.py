from typer.testing import CliRunner
from thread_safety_linter.cli import app

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
