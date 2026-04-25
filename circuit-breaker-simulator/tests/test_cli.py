import typer
from click.testing import CliRunner
from circuit_breaker_simulator.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Run circuit breaker simulation" in result.stdout

# Full e2e would require patching sim, but core logic tested


def test_run_defaults():
    # Patches would be in integration, but CLI parses ok
    result = runner.invoke(app, ["run", "--rps", "1", "--duration", "1"])
    assert result.exit_code == 0
