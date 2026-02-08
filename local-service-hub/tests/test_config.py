import tomllib
from pathlib import Path
from local_service_hub.config import load_config, merge_configs


def test_merge_configs(tmp_path: Path):
    default = {"a": 1, "b": {"x": 10}}
    user = {"a": 2, "b": {"y": 20}, "c": 3}
    merged = merge_configs(default, user)
    assert merged == {"a": 2, "b": {"x": 10, "y": 20}, "c": 3}


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "wb") as f:
        tomllib.dump({"services": {"postgres": {"enabled": False}}}, f)
    # Simulate cwd
    assert load_config() == {}  # no file

# Note: full integration needs file system mocks
