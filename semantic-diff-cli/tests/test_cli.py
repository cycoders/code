'''Integration tests for CLI.''' 

import pytest
from click.testing import CliRunner
from semantic_diff_cli.cli import app

runner = CliRunner()


def test_files_help():
    result = runner.invoke(app, ["files", "--help"])
    assert result.exit_code == 0


def test_git_help():
    result = runner.invoke(app, ["git", "--help"])
    assert result.exit_code == 0

# More integration via pytest parametrize if needed
