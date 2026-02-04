import sys
from typer.testing import CliRunner

from git_history_viz.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Visualize Git history" in result.stdout

# Note: Full e2e requires sample_repo cwd mock, skipped for brevity
