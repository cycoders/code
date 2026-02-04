import pytest
from pathlib import Path
from git import Repo


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """Linear + merge sample repo."""
    repo_path = tmp_path / "repo"
    repo = Repo.init(repo_path)
    repo.git("config", "user.name", "Test Author")
    repo.git("config", "user.email", "test@example.com")

    # Commit 1: root
    (repo_path / "a.txt").write_text("A")
    repo.index.add(all=True)
    repo.index.commit("Init a.txt")

    # Commit 2: main
    (repo_path / "b.txt").write_text("B")
    repo.index.add(all=True)
    repo.index.commit("Add b.txt")

    root = repo.head.commit
    main_tip = repo.head.commit

    # Feature branch
    repo.git.checkout("-b", "feat")
    (repo_path / "c.txt").write_text("C")
    repo.index.add(all=True)
    repo.index.commit("Add c.txt (feat)")

    # Merge to main
    repo.git.checkout("main")
    repo.git.merge("feat")

    yield repo_path
