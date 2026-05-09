from pathlib import Path
import pytest
from csp_policy_builder.config import load_config, ScanConfig


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
urls:
  - https://test.com
max_depth: 1
""")

    cfg = load_config(config_path)
    assert cfg.urls == ["https://test.com"]
    assert cfg.max_depth == 1


def test_invalid_config():
    with pytest.raises(ValueError):
        ScanConfig(urls=[])
