import pytest
from click.testing import CliRunner
from perf_guard.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout

# Note: Full e2e needs mocks; smoke test pass

def test_baseline_help():
    result = runner.invoke(app, ["baseline", "--help"])
    assert result.exit_code == 0