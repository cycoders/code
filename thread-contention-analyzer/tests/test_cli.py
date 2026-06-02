from click.testing import CliRunner
from thread_contention_analyzer.cli import main

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["--duration", "0.1"])
    assert result.exit_code == 0