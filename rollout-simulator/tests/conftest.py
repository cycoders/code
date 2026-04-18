import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

import rollout_simulator
from rollout_simulator.cli import app
from rollout_simulator.sample import generate_sample


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def sample_metrics(tmp_path: Path) -> Path:
    p = tmp_path / "metrics.jsonl"
    p.write_text(generate_sample())
    return p


SAMPLE_JSONL = generate_sample()