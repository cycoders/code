import pytest
from ab_test_calculator_cli.cli import cli
from typer.testing import CliRunner

runner = CliRunner()


def test_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Design" in result.stdout


def test_design_prop_valid():
    result = runner.invoke(
        cli, ["design", "prop", "0.05", "0.01", "--alpha", "0.05", "--power", "0.8"]
    )
    assert result.exit_code == 0
    assert "15,708" in result.stdout


def test_design_prop_invalid_baseline():
    result = runner.invoke(cli, ["design", "prop", "1.5", "0.01"])
    assert result.exit_code == 1
    assert "Baseline must be in (0,1)" in result.stdout


def test_analyze_valid():
    result = runner.invoke(cli, ["analyze", "100", "1000", "120", "1000"])
    assert result.exit_code == 0
    assert "0.240" in result.stdout
    assert "0.78" in result.stdout