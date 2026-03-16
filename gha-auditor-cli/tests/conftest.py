import pytest
from pathlib import Path
from typer.testing import CliRunner

from gha_auditor_cli.cli import app

runner = CliRunner()

@pytest.fixture
def runner_fixture():
    return runner

@pytest.fixture
def sample_workflows_dir() -> Path:
    return Path(__file__).parent / "data"
