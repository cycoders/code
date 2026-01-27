import pytest
import subprocess
from pathlib import Path


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    """Minimal repo with small + large file."""
    repo = tmp_path / "minirepo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)

    # Small file
    (repo / "small.txt").write_text("hello world")
    subprocess.run(["git", "add", "small.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "add small"], cwd=repo, check=True)

    # Large file
    large_file = repo / "large.bin"
    large_file.write_bytes(b"\x00" * (5 * 1024 * 1024))  # 5 MiB
    subprocess.run(["git", "add", "large.bin"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "add large"], cwd=repo, check=True)

    # Tag
    subprocess.run(["git", "tag", "v1.0"], cwd=repo, check=True)

    return repo


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Empty Git repo (edge case)."""
    repo = tmp_path / "emptyrepo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    return repo