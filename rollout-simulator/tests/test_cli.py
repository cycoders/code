from pathlib import Path
import pytest
from typer.testing import CliRunner

from rollout_simulator.cli import app


def test_generate_sample(runner: CliRunner, tmp_path: Path):
    out_path = tmp_path / "test.jsonl"
    result = runner.invoke(app, ["generate-sample", str(out_path)])
    assert result.exit_code == 0
    assert "Wrote" in result.stdout
    assert out_path.exists()
    assert len(out_path.read_text().splitlines()) == 30


def test_analyze(runner: CliRunner, sample_metrics: Path):
    result = runner.invoke(app, ["analyze", str(sample_metrics), "--sims", "100", "--threshold", "0.01"])
    assert result.exit_code == 0
    assert "Loaded" in result.stdout
    assert "Recommended" in result.stdout
    assert "Risk" in result.stdout


def test_analyze_invalid_file(runner: CliRunner, tmp_path: Path):
    bad = tmp_path / "nope.jsonl"
    result = runner.invoke(app, ["analyze", str(bad)])
    assert result.exit_code == 1
    assert "not found" in result.stdout