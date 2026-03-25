import pytest
from pathlib import Path
from pem_tool_cli.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_convert_help():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "pkcs8" in result.stdout

# Integration test stub; requires real key PEM
# assert output file format matches expected