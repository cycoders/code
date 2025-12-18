import pytest
from typer.testing import CliRunner

from cron_simulator.cli import app

runner = CliRunner()


def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Simulate" in result.stdout


def test_sim_help():
    result = runner.invoke(app, ["sim", "--help"])
    assert result.exit_code == 0


def test_predict_valid():
    result = runner.invoke(app, ["predict", "--cron", "* * * * *", "--count", "1"])
    assert result.exit_code == 0


def test_validate_invalid():
    result = runner.invoke(app, ["validate", "invalid-cron"])
    assert result.exit_code != 0