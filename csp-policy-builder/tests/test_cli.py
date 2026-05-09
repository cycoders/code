import pytest
from click.testing import CliRunner
from csp_policy_builder.cli import app


runner = CliRunner()


def test_cli_version(mocker):
    mocker.patch("csp_policy_builder.cli.__version__", "0.1.0")
    result = runner.invoke(app, ["scan", "https://test", "--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.stdout
