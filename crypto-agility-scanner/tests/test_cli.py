from click.testing import CliRunner
from crypto_agility_scanner.cli import main

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "--help"])
    assert result.exit_code == 0