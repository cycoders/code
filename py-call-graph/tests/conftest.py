import pytest
from typer.testing import CliRunner
from py_call_graph.main import app

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def invoke(runner):
    return runner.invoke(app)