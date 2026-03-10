import pytest
from typer.testing import CliRunner
from git_submodule_auditor.cli import app

runner = CliRunner()


def test_list_help():
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "List submodules" in result.stdout


def test_audit_help():
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0


def test_graph_help():
    result = runner.invoke(app, ["graph", "--help"])
    assert result.exit_code == 0


def test_update_help():
    result = runner.invoke(app, ["update", "--help"])
    assert result.exit_code == 0


def test_app_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
