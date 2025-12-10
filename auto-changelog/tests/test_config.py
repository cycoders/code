import pytest
from pathlib import Path
from auto_changelog.config import load_config, DEFAULT_CONFIG


@pytest.fixture
def temp_config(tmp_path: Path):
    config_path = tmp_path / ".auto-changelog.yaml"
    config_path.write_text("""
type_to_section:
  feat: Custom Added
""")
    return config_path


def test_load_default():
    assert load_config(None) == DEFAULT_CONFIG


def test_load_custom(temp_config):
    cfg = load_config(temp_config)
    assert cfg["type_to_section"]["feat"] == "Custom Added"
    assert "fix" in cfg["type_to_section"]