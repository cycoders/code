import os
import tomllib
from pathlib import Path

from rate_limit_tester.config import Config, load_config


def test_load_config_overrides(tmp_path: Path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('''
[default]
url = "https://test.com"
    ''')

    os.environ["RLT_AUTH_TOKEN"] = "fake"
    cfg = load_config(config_path, overrides={"concurrency": 5})

    assert cfg.url == "https://test.com"
    assert cfg.headers["Authorization"] == "Bearer fake"
    assert cfg.concurrency == 5
