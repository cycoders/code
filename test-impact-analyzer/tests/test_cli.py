from typer.testing import CliRunner
from test_impact_analyzer.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "impacted" in result.output.lower()