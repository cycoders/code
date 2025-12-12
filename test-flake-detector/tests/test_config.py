import pytest
from pathlib import Path

from test_flake_detector.config import load_config


def test_load_config_defaults(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "missing.toml")
    assert cfg == {}


@pytest.fixture
def sample_config(tmp_path: Path) -> Path:
    cfg_file = tmp_path / "flake.toml"
    cfg_file.write_text('num_runs = 20\nthreshold = 0.1\npytest_args = ["tests/"]')
    return cfg_file


def test_load_config_values(sample_config: Path) -> None:
    cfg = load_config(sample_config)
    assert cfg["num_runs"] == 20
    assert cfg["threshold"] == 0.1
    assert cfg["pytest_args"] == ["tests/"]