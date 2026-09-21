from click.testing import CliRunner
from typosquat_auditor.cli import cli

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0