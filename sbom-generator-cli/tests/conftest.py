import pytest
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fixture for temp project dir."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").touch()  # Example marker
    return tmp_path
