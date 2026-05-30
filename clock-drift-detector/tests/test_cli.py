from click.testing import CliRunner
from clock_drift_detector.cli import cli

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0