from click.testing import CliRunner
from migration_safety_analyzer.cli import main

def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0