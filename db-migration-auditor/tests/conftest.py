import pytest
from typer.testing import CliRunner
from db_migration_auditor.cli import app

runner = CliRunner()


@pytest.fixture
def cli_runner():
    return runner