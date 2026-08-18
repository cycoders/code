from click.testing import CliRunner
from thread_pool_calibrator.cli import cli

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0