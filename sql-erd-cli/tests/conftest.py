import pytest
from typer.testing import CliRunner

from sql_erd_cli.cli import app

runner = CliRunner()


@pytest.fixture
def cli_runner():
    return runner