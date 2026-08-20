from click.testing import CliRunner
from dotenv_linter.cli import cli

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0