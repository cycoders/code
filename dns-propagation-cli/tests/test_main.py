import pytest
from typer.testing import CliRunner
from dns_propagation_cli.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Check DNS propagation status" in result.stdout


def test_check_minimal(mocker):
    mocker.patch(
        "dns_propagation_cli.main.check_propagation",
        return_value=[],
    )
    result = runner.invoke(
        app, ["check", "example.com", "--expected", "1.1.1.1"]
    )
    assert result.exit_code == 0


def test_bad_domain():
    result = runner.invoke(app, ["check", "", "--expected", "1.1.1.1"])
    assert result.exit_code != 0