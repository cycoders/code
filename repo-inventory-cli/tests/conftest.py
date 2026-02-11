import pytest
from pathlib import Path
from git import Repo


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "testrepo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    (repo_path / "main.py").write_text("print('hello')\n")
    (repo_path / "README.md").write_text("# Test")
    repo.git.add(A=True)
    repo.index.commit("Initial commit")
    repo.git.checkout("-b", "feature")
    return repo_path


@pytest.fixture
def dirty_repo(sample_repo):
    (sample_repo / "new.txt").write_text("dirty")
    return sample_repo


@pytest.fixture
def orphaned_repo(tmp_path: Path) -> Path:
    repo_path = tmp_path / "orphaned"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    (repo_path / "file.txt").write_text("orphaned")
    repo.git.add(A=True)
    repo.index.commit("commit")
    return repo_path
