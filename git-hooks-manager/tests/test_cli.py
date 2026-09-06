from typer.testing import CliRunner
from git_hooks_manager.cli import app

def test_init():
    runner = CliRunner()
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0