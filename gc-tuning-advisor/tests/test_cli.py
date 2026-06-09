from click.testing import CliRunner
from gc_tuning_advisor.cli import main

def test_cli_runs():
    runner = CliRunner()
    result = runner.invoke(main, ['analyze', '-'])
    assert result.exit_code == 0