from typer.testing import CliRunner
from async_deadline_linter.cli import app

def test_cli_invocation():
    runner = CliRunner()
    result = runner.invoke(app, ["."])
    assert result.exit_code == 0