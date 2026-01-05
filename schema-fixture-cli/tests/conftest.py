import pytest
from typer.testing import CliRunner

from schema_fixture_cli.cli import app


@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def set_random_seed():
    import random
    random.seed(42)
