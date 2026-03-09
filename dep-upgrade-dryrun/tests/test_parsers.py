import pytest
from upgrade_dryrun.parsers import parse_npm_lock, parse_poetry_lock, parse_cargo_lock
from pathlib import Path


def test_parse_npm_lock(sample_data_dir: Path):
    lock_path = sample_data_dir / "npm" / "package-lock.json"
    deps, total_size, sizes = parse_npm_lock(lock_path)
    assert "lodash" in deps
    assert deps["lodash"] == "4.17.21"
    assert "express" in deps
    assert total_size == 1401024 + 512000
    assert sizes["lodash"] == 1401024


def test_parse_poetry_lock(sample_data_dir: Path):
    lock_path = sample_data_dir / "poetry" / "poetry.lock"
    deps, total_size, sizes = parse_poetry_lock(lock_path)
    assert "requests" in deps
    assert deps["requests"] == "2.31.0"
    assert "certifi" in deps
    assert total_size is None
    assert sizes is None


def test_parse_cargo_lock(sample_data_dir: Path):
    lock_path = sample_data_dir / "cargo" / "Cargo.lock"
    deps, total_size, sizes = parse_cargo_lock(lock_path)
    assert "serde" in deps
    assert deps["serde"] == "1.0.193"
    assert "tokio" in deps
    assert total_size is None
    assert sizes is None
