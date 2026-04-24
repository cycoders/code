import pytest
from typer.testing import CliRunner

from password_strength_simulator.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_list_hardware():
    result = runner.invoke(app, ["list", "hardware"])
    assert result.exit_code == 0
    assert "rtx4090" in result.stdout


@pytest.mark.parametrize("invalid", ["foo", "--invalid"])
def test_errors(invalid: str):
    result = runner.invoke(app, ["estimate", "pw", invalid])
    assert result.exit_code != 0
    assert "Error" in result.stdout