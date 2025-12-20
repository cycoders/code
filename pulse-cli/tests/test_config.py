import pytest
from pathlib import Path
from pulse_cli.config import load_config, PulseConfig


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
endpoints:
  - name: test
    url: https://test.com
""")
    config = load_config(config_path)
    assert isinstance(config, PulseConfig)
    assert len(config.endpoints) == 1


def test_missing_config():
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))