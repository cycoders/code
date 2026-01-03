import pytest
from typer.testing import CliRunner
from tls_inspector.cli import cli

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Inspect" in result.stdout


def test_cli_inspect_help():
    result = runner.invoke(cli, ["inspect", "--help"])
    assert result.exit_code == 0
    assert "host" in result.stdout


def test_cli_unknown_command():
    result = runner.invoke(cli, ["foo"])
    assert result.exit_code == 2
    assert "Error: No such command" in result.stderr


def test_cli_port_validation():
    result = runner.invoke(cli, ["inspect", "example.com", "--port", "99999"])
    assert result.exit_code == 2
    assert "port" in result.stderr