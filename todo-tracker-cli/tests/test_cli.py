import pytest
from typer.testing import CliRunner

from todo_tracker_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0
    assert 'Scan codebase' in result.stdout


@pytest.mark.parametrize('args,expected', [
    (['--version'], 0),
    (['nonexistent'], 2),
])
def test_cli_errors(args, expected):
    result = runner.invoke(app, args)
    assert result.exit_code == expected