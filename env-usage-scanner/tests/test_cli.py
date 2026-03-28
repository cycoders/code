import pytest
from click.testing import CliRunner

from env_usage_scanner.cli import app


runner = CliRunner()


def test_cli_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan directory" in result.stdout

# Full integration would mock paths, but smoke test ok
