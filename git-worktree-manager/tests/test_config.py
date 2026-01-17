import pytest
from pathlib import Path
from git_worktree_manager.config import load_config, get_config_path
import os

@pytest.fixture
def mock_xdg(monkeypatch, tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "git-worktree-manager" / "config.toml"
    config_path.parent.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))
    return config_path

def test_load_config_default(mock_xdg):
    assert load_config() == {}

def test_load_config_content(mock_xdg):
    mock_xdg.write_text('[core]\ndefault_from = "origin/develop"')
    config = load_config()
    assert config["core"]["default_from"] == "origin/develop"