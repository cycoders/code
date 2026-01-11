import pytest
from pathlib import Path
from dep_tree_viz.detector import detect_lockfile


@pytest.fixture
def tmp_project(tmp_path: Path):
    return tmp_path


def test_detect_poetry(tmp_project: Path):
    (tmp_project / "poetry.lock").touch()
    result = detect_lockfile(tmp_project)
    assert result[0] == "poetry"


def test_detect_npm(tmp_project: Path):
    (tmp_project / "package-lock.json").touch()
    result = detect_lockfile(tmp_project)
    assert result[0] == "npm"


def test_detect_cargo(tmp_project: Path):
    (tmp_project / "Cargo.lock").touch()
    result = detect_lockfile(tmp_project)
    assert result[0] == "cargo"


def test_no_lock(tmp_project: Path):
    assert detect_lockfile(tmp_project) is None


def test_priority(tmp_project: Path):
    (tmp_project / "poetry.lock").touch()
    (tmp_project / "package-lock.json").touch()
    result = detect_lockfile(tmp_project)
    assert result[0] == "poetry"  # First wins