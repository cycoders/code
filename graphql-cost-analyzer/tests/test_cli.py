from typer.testing import CliRunner
from graphql_cost_analyzer.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_analyze_runs():
    result = runner.invoke(app, ["analyze", "schema.graphql", "q.graphql"])
    assert "Analyzed" in result.output