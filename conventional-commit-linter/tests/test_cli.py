import pytest
from typer.testing import CliRunner
from conventional_commit_linter.cli import app

runner = CliRunner()


def test_lint_help():
    result = runner.invoke(app, ["lint", "--help"])
    assert result.exit_code == 0
    assert "Lint commit(s)" in result.stdout


def test_install_hook_help():
    result = runner.invoke(app, ["install-hook", "--help"])
    assert result.exit_code == 0
