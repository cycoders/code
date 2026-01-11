import pytest
from typer.testing import CliRunner
from dep_tree_viz.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI --help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Visualize dependency tree" in result.stdout


def test_cli_version():
    """Test no-args invokes help."""
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_invalid_format():
    """Test invalid format errors gracefully."""
    result = runner.invoke(app, [".", "--format", "foo"])
    assert result.exit_code == 1
    assert "Unsupported format" in result.stderr