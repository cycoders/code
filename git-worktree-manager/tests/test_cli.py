import typer
from click.testing import CliRunner
from git_worktree_manager.cli import app

runner = CliRunner()

def test_list_help():
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0

# Integration relies on git mocks in conftest