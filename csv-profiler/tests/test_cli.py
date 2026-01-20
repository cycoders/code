import pytest
from click.testing import CliRunner
from csv_profiler.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "profile" in result.stdout

# Integration via profiler tests