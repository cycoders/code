from typer.testing import CliRunner
from exception_graph_cli.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "exception graph" in result.output.lower()