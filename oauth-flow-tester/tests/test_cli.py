import pytest
from typer.testing import CliRunner
from oauth_flow_tester.cli import app

runner = CliRunner()


def test_server_help():
    result = runner.invoke(app, ["server", "--help"])
    assert result.exit_code == 0
    assert "Run the mock OAuth" in result.stdout


def test_auth_code_help():
    result = runner.invoke(app, ["auth-code", "--help"])
    assert result.exit_code == 0
    assert "Simulate full authorization" in result.stdout


def test_client_credentials_help():
    result = runner.invoke(app, ["client-credentials", "--help"])
    assert result.exit_code == 0


def test_inspect_help():
    result = runner.invoke(app, ["inspect", "--help"])
    assert result.exit_code == 0


def test_no_args_help():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
