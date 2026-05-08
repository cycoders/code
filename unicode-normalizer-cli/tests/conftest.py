import pytest
from pathlib import Path
import git

@pytest.fixture
def tmp_git_repo(tmp_path: Path):
    """Tmp git repo fixture."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)
    (repo_path / "test.py").write_text("caf\u0301e\n")
    (repo_path / "caf\u0301e.md").write_text("# Title")
    repo.git.add(A=True)
    repo.git.commit("-m", "init")
    return repo_path, repo