import pytest
from pathlib import Path

from deadcode_hunter.config import Config, load_config


@pytest.fixture
def temp_toml(tmp_path: Path):
    toml_path = tmp_path / ".deadcodehunter.toml"
    toml_path.write_text(
        "[tool.deadcode-hunter]\nignores = ['custom/']\nmin-confidence = 80"
    )
    return toml_path


def test_default_config():
    cfg = load_config()
    assert "tests" in cfg.ignores
    assert cfg.min_confidence == 50


def test_load_custom_config(temp_toml):
    cfg = load_config(str(temp_toml))
    assert "custom/" in cfg.ignores
    assert cfg.min_confidence == 80


def test_pyproject_toml(tmp_path: Path):
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text("[tool.deadcode-hunter]\nignores = ['docs/']")
    cfg = load_config()
    assert "docs/" in cfg.ignores
