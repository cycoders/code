import pytest
import subprocess
from pathlib import Path

@pytest.fixture(scope="session")
def git_repo(tmp_path_factory) -> Path:
    """Fixture: a temp git repo with branches for merge testing."""
    repo_path = tmp_path_factory.mktemp("repo")
    subprocess.run(["git", "init", str(repo_path)], check=True, capture_output=True)

    # Base commit
    (repo_path / "file.txt").write_text("base content\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial base"], cwd=repo_path, check=True)

    # Branch 1: modify file
    subprocess.run(["git", "checkout", "-b", "branch1"], cwd=repo_path, check=True)
    (repo_path / "file.txt").write_text("branch1 content\n")
    subprocess.run(["git", "commit", "-am", "branch1 change"], cwd=repo_path, check=True)

    # Back to main
    subprocess.run(["git", "checkout", "-B", "main"], cwd=repo_path, check=True)

    # Branch 2: conflicting modify
    subprocess.run(["git", "checkout", "-b", "branch2"], cwd=repo_path, check=True)
    (repo_path / "file.txt").write_text("branch2 content\n")
    subprocess.run(["git", "commit", "-am", "branch2 change"], cwd=repo_path, check=True)

    # Non-conflicting file on branch2
    (repo_path / "newfile.txt").write_text("new on branch2\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-am", "add newfile"], cwd=repo_path, check=True)

    return repo_path