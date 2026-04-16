import pytest
from click.testing import CliRunner

from shell_history_analyzer.cli import app


runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


# Note: Full CLI tests with files use fixtures, typer echo testable
