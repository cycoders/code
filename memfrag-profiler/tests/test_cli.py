from typer.testing import CliRunner
from memfrag_profiler.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_attach():
    result = runner.invoke(app, ["attach", "--pid", "1", "--duration", "0.1s"])
    assert "Attaching" in result.output