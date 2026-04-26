import pytest
from typer.testing import CliRunner
from env_dependency_analyzer.cli import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0

# More integration needs fixtures, but CLI parses

def test_viz_help():
    result = runner.invoke(app, ["viz", "--help"])
    assert result.exit_code == 0


def test_check_help():
    result = runner.invoke(app, ["check", "--help"])
    assert result.exit_code == 0
