import pytest
from typer.testing import CliRunner

from ab_test_calculator_cli.cli import cli

runner = CliRunner()


@pytest.fixture
def invoke():
    def _invoke(*args, **kwargs):
        return runner.invoke(cli, [*args], **kwargs)
    return _invoke