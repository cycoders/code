from typer.testing import CliRunner
from config_consistency_checker.cli import app

def test_cli_help():
    result = CliRunner().invoke(app, ['--help'])
    assert result.exit_code == 0