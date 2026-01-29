import pytest
from typer.testing import CliRunner
from http_signer_cli.cli import app

runner = CliRunner()

@pytest.fixture
def invoke_cli():
    def _invoke(*args, **kwargs):
        return runner.invoke(app, [*args], **kwargs)
    return _invoke