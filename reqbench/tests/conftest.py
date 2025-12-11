import pytest
from typer.testing import CliRunner
from reqbench.cli import app

runner = CliRunner()

@pytest.fixture
def invoke():
    return runner.invoke(app)