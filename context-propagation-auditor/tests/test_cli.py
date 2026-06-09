from typer.testing import CliRunner
from context_propagation_auditor.cli import app

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["."])
    assert result.exit_code in (0, 1)