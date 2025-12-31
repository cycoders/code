import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from har_analyzer.cli import app

runner = CliRunner()

@pytest.fixture
def sample_har_path() -> Path:
    return Path(__file__).parent / "data" / "sample.har"

@pytest.fixture
def sample_entries():
    return json.loads(Path(__file__).parent / "data" / "sample.har").get("log", {}).get("entries", [])