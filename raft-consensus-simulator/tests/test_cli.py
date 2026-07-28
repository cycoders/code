from typer.testing import CliRunner
from raft_consensus_simulator.cli import app

runner = CliRunner()

def test_run_command():
    result = runner.invoke(app, ["run", "--nodes", "3", "--steps", "5"])
    assert result.exit_code == 0