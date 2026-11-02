from typer.testing import CliRunner
from middleware_order_linter.cli import app

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0