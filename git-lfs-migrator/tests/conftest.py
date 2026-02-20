import pytest
from typer.testing import CliRunner
from git_lfs_migrator.cli import app


@pytest.fixture
def runner():
    return CliRunner()
