import typer
from typer.testing import CliRunner

from leader_election_simulator.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Run Raft" in result.stdout


def test_cli_run():
    result = runner.invoke(app, ["run", "--num-nodes", "3", "--duration", "10", "--batch"])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "Elections" in result.stdout