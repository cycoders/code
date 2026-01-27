import pytest
from typer.testing import CliRunner
from formatter_preview.cli import app

runner = CliRunner()


@pytest.fixture
def cli_runner():
    return runner

@pytest.fixture
def mock_subprocess(monkeypatch):
    def mock_run(cmd, *args, **kwargs):
        from subprocess import CompletedProcess
        return CompletedProcess(cmd, 0, stdout=b'', stderr=b'')
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run
