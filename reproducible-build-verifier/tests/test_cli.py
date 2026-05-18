from click.testing import CliRunner
from reproducible_build_verifier.cli import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0

def test_compare_invocation():
    runner = CliRunner()
    result = runner.invoke(cli, ['compare', '--help'])
    assert 'Compare two build artifacts' in result.output