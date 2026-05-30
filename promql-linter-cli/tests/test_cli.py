from typer.testing import CliRunner
from promql_linter_cli.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0