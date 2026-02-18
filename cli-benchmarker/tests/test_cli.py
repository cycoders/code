import shlex
from typer.testing import CliRunner

from cli_benchmarker.cli import app

runner = CliRunner()


def test_run_help():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "Benchmark CLI commands" in result.stdout


def test_no_commands(monkeypatch):
    # Patch shlex to avoid real exec
    monkeypatch.setattr("sys.exit", lambda x: None)
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 1
    assert "Provide at least one command" in result.stderr


def test_single_command(monkeypatch):
    def mock_benchmark(*args, **kwargs):
        return [{"success": True, "wall_time": 0.1}]
    monkeypatch.setattr("cli_benchmarker.benchmark.benchmark_commands", mock_benchmark)
    monkeypatch.setattr("cli_benchmarker.reporter.print_results", lambda x: None)

    result = runner.invoke(app, ["run", "echo hello"])
    assert result.exit_code == 0