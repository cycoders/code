import pytest
from typer.testing import CliRunner

from queue_simulator.cli import app

runner = CliRunner()

@pytest.fixture
def invoke():
    def _invoke(*args):
        return runner.invoke(app, [*args])
    return _invoke