import pytest
from click.testing import CliRunner

from shell_auditor_cli.cli import app


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit a shell script" in result.stdout


# Note: Full integration via core tests