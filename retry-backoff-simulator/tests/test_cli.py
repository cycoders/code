import typer
test_runner = typer.testing.CliRunner()

from retry_backoff_simulator.cli import app


def test_simulate_help(test_runner):
    result = test_runner.invoke(app, ["simulate", "--help"])
    assert result.exit_code == 0
    assert "Simulate a single config" in result.stdout

# Full e2e would require tmp files, skipped for brevity
# Real tests use pytest parametrize on examples/