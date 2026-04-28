import os
import tempfile
from pathlib import Path
import pytest
import git


@pytest.fixture(scope="function")
def sample_repo() -> Path:
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        repo = git.Repo.init(repo_path)
        repo.git.config("--local", "user.name", "Test Author")
        repo.git.config("--local", "user.email", "test@example.com")

        # File for commits
        f1 = repo_path / "file1.txt"

        # Alice commit 1
        f1.write_text("initial\n")
        repo.index.add("file1.txt")
        repo.index.commit(
            "Initial commit",
            author_name="Alice",
            author_email="alice@example.com",
        )

        # Alice commit 2 (some adds)
        old_content = f1.read_text()
        f1.write_text(old_content + "added line1\nadded line2\n")
        repo.index.add("file1.txt")
        repo.index.commit(
            "Add lines",
            author_name="Alice",
            author_email="alice@example.com",
        )

        # Bob commit
        f1.write_text(old_content + "bob line\n")
        repo.index.add("file1.txt")
        repo.index.commit(
            "Bob contrib",
            author_name="Bob",
            author_email="bob@example.com",
        )

        yield repo_path
