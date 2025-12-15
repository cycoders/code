import pytest
from typer.testing import CliRunner

from regex_playground_cli.cli import app


@pytest.fixture
 def runner():
    yield CliRunner()
