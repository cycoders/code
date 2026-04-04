import pytest
from pathlib import Path

from connection_pool_simulator.config import SimConfig, get_config


def test_default_config():
    cfg = SimConfig()
    assert cfg.max_size == 10
    assert cfg.acquire_timeout == 1.0


def test_get_config_file(tmp_path: Path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("max_size: 5\nnum_clients: 20")
    cfg = get_config(yaml_file)
    assert cfg.max_size == 5
    assert cfg.num_clients == 20


def test_get_config_override():
    cfg = get_config(None, max_size=15, num_clients=30)
    assert cfg.max_size == 15
    assert cfg.num_clients == 30


def test_get_config_file_override(tmp_path: Path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("max_size: 5")
    cfg = get_config(yaml_file, num_clients=99)
    assert cfg.max_size == 5
    assert cfg.num_clients == 99


def test_invalid_config(tmp_path: Path):
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text("max_size: -1")
    with pytest.raises(ValueError):
        get_config(yaml_file)
