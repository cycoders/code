from click.testing import CliRunner
from observability_gap_detector.cli import main

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0