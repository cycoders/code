from typer.testing import CliRunner
from timeout_advisor.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "timeout" in result.output