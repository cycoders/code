from typer.testing import CliRunner
from query_plan_diff_cli.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0