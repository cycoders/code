import sys
from click.testing import CliRunner
from ratelimit_simulator.cli import app

runner = CliRunner()


def test_tui_help():
    result = runner.invoke(app, ["tui", "--help"])
    assert result.exit_code == 0
    assert "Interactive TUI simulator" in result.stdout


def test_simulate_help():
    result = runner.invoke(app, ["simulate", "--help"])
    assert result.exit_code == 0
    assert "Run non-interactive simulation" in result.stdout


def test_simulate_valid(monkeypatch):
    # Mock run_simulation to avoid real compute
    def mock_run(*args, **kwargs):
        from ratelimit_simulator.simulator import Stats
        return Stats(hit_rate=0.9, total_requests=100, accepted=90, rejected=10, max_burst=5)
    monkeypatch.setattr("ratelimit_simulator.simulator.run_simulation", mock_run)

    result = runner.invoke(app, ["simulate", "token", "-l", "10"])
    assert result.exit_code == 0
    assert "Hit Rate" in result.stdout
    assert "90.0%" in result.stdout


def test_simulate_invalid():
    result = runner.invoke(app, ["simulate", "invalid"])
    assert result.exit_code != 0
    assert "Unknown policy" in result.stdout
