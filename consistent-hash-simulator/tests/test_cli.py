from click.testing import CliRunner
from consistent_hash_simulator.cli import cli

def test_run_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--nodes", "2", "--keys", "100"])
    assert result.exit_code == 0