import pytest
from typer.testing import CliRunner

from strace_analyzer.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout


# Note: full CLI tests require mocks for files
