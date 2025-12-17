import pytest
from pathlib import Path


@pytest.fixture
def simple_proj(tmp_path: Path) -> Path:
    """Simple acyclic project."""
    proj = tmp_path / "simple"
    proj.mkdir()
    (proj / "main.py").write_text("from .utils import helper")
    (proj / "utils.py").write_text("def helper(): pass")
    return proj


@pytest.fixture
def cycle_proj(tmp_path: Path) -> Path:
    """Project with cycle: a -> b -> a."""
    proj = tmp_path / "cycle"
    proj.mkdir()
    (proj / "a.py").write_text("from b import x")
    (proj / "b.py").write_text("from a import something")
    return proj
