import sys
from click.testing import CliRunner

from redos_detector.cli import app


runner = CliRunner()


def test_check_help():
    result = runner.invoke(app, ["check", "--help"])
    assert result.exit_code == 0
    assert "Check a regex" in result.stdout


def test_check_invalid_regex():
    result = runner.invoke(app, ["check", "[unclosed"])
    assert result.exit_code == 1
    assert "Invalid regex" in result.stdout


def test_bench_runs():
    result = runner.invoke(app, ["bench"])
    assert result.exit_code == 0
    assert "Benchmarks" in result.stdout
