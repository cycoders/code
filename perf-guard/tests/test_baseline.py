import json
import pytest
from pathlib import Path

from perf_guard.baseline import get_baseline_path, load_baseline, save_baseline
from perf_guard.stats import compute_stats


@pytest.fixture
def baseline_dir(tmp_path: Path):
    dir = tmp_path / ".perfguard-baselines"
    dir.mkdir()
    return dir


def test_save_load(baseline_dir: Path):
    name = "test"
    times = [1.0, 1.1]
    stats = compute_stats(times)

    save_baseline(name, stats, "test cmd")

    path = get_baseline_path(name)
    assert path.exists()

    loaded = load_baseline(name)
    assert loaded == stats
    assert loaded["command"] == "test cmd"


def test_load_missing(baseline_dir: Path):
    assert load_baseline("missing") is None


def test_invalid_json(baseline_dir: Path):
    path = get_baseline_path("invalid")
    path.write_text("{}")
    loaded = load_baseline("invalid")
    assert loaded is None  # Would raise on strict, but safe
