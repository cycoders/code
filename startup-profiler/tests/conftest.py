import pytest
from typer.testing import CliRunner
from startup_profiler.cli import app

@pytest.fixture
runner = CliRunner()
