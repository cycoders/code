from click.testing import CliRunner
from pyc_disassembler_cli.cli import main

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0