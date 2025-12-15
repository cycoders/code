import pytest
from pathlib import Path

from deadcode_hunter.finder import find_python_files


@pytest.fixture
def sample_dir(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()
    (tmp_path / "tests" / "test.py").mkdir(parents=True)
    (tmp_path / "tests" / "test.py").touch()
    return tmp_path


def test_find_python_files(sample_dir):
    ignores = ["tests"]
    files = list(find_python_files(str(sample_dir), ignores))
    assert len(files) == 1
    assert files[0].name == "main.py"


def test_no_ignores(sample_dir):
    files = list(find_python_files(str(sample_dir), []))
    assert len(files) == 2
