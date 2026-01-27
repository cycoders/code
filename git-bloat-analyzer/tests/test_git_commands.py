import pytest
from pathlib import Path

from git_bloat_analyzer.git_commands import run_git, is_git_repo


def test_is_git_repo_valid(mini_repo: Path):
    assert is_git_repo(mini_repo)


def test_is_git_repo_invalid(tmp_path: Path):
    assert not is_git_repo(tmp_path / "nonexistent")
    assert not is_git_repo(tmp_path)


def test_run_git_success(mini_repo: Path):
    output = run_git(["rev-parse", "--is-inside-work-tree"], mini_repo)
    assert "true" in output


def test_run_git_fails_gracefully(mini_repo: Path):
    with pytest.raises(RuntimeError, match="git status --invalid"):
        run_git(["status", "--invalid"], mini_repo)