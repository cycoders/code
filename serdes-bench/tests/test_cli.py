import pytest
from typer.testing import CliRunner

from serdes_bench.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Benchmark" in result.stdout


def test_generate_simple():
    result = runner.invoke(app, ["--generate", "simple", "--size", "10"])
    assert result.exit_code == 0


def test_bad_generate():
    result = runner.invoke(app, ["--generate", "invalid"])
    assert result.exit_code != 0
    assert "Unknown kind" in result.stdout
