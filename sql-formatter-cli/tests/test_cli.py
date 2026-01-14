'''CLI integration tests.''' 

import subprocess
import sys
from pathlib import Path
from typer.testing import CliRunner

from sql_formatter_cli.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_stdin(tmp_path):
    result = runner.invoke(app, input="select * from t", standalone_mode=False)
    assert result.exit_code == 0
    assert "SELECT" in result.stdout

# Note: Full file/dir tests require fs mocks, covered by formatter + manual


def test_invalid_flag():
    result = runner.invoke(app, ["--invalid"])
    assert result.exit_code != 0
