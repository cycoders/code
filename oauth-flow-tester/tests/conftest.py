import pytest
from typer.testing import CliRunner
from oauth_flow_tester.cli import app

runner = CliRunner()

@pytest.fixture
def cli_runner():
    return runner

@pytest.fixture
def mock_console(mocker):
    return mocker.patch("rich.console.Console")
