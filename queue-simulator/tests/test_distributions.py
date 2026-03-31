import pytest
from pathlib import Path
import random

from queue_simulator.distributions import load_durations, get_service_sampler


def test_load_durations(tmp_path: Path):
    csv_file = tmp_path / "jobs.csv"
    csv_file.write_text("0.1\n0.2\n0.15\ninvalid\n0.3")
    durs = load_durations(csv_file)
    assert len(durs) == 4
    assert all(0.1 <= d <= 0.3 for d in durs)


def test_load_durations_empty(tmp_path: Path):
    csv_file = tmp_path / "empty.csv"
    csv_file.touch()
    with pytest.raises(ValueError, match="No valid durations"):
        load_durations(csv_file)


def test_load_durations_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_durations(tmp_path / "missing.csv")


def test_sampler_fixed():
    rng = random.Random(42)
    sampler = get_service_sampler("fixed", {"service_mean": 0.1}, rng)
    assert sampler() == 0.1


def test_sampler_exp():
    rng = random.Random(42)
    sampler = get_service_sampler("exp", {"service_mean": 0.1}, rng)
    samples = [sampler() for _ in range(10)]
    assert all(s > 0 for s in samples)


def test_sampler_empirical(tmp_path: Path):
    csv_file = tmp_path / "jobs.csv"
    csv_file.write_text("0.1\n0.2")
    rng = random.Random(42)
    sampler = get_service_sampler("empirical", {"service_file": csv_file}, rng)
    assert sampler() in (0.1, 0.2)