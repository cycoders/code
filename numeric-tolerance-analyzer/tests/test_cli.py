from click.testing import CliRunner
from numeric_tolerance_analyzer.cli import main

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["src"])
    assert result.exit_code == 0