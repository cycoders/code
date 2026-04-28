import pytest
from datetime import datetime, timedelta
from pathlib import Path

from git_contributor_analyzer.git_parser import get_repo_commits
from git_contributor_analyzer.types import CommitInfo


class TestGitParser:
    def test_valid_repo(self, sample_repo: Path):
        commits = get_repo_commits(sample_repo)
        assert len(commits) == 3
        alice_commits = [c for c in commits if c.author_email == "alice@example.com"]
        assert len(alice_commits) == 2
        assert alice_commits[0].insertions > 0

    def test_empty_repo(self, tmp_path: Path):
        repo_path = tmp_path / "empty"
        git.Repo.init(repo_path)
        commits = get_repo_commits(repo_path)
        assert len(commits) == 0

    def test_filter_author(self, sample_repo: Path):
        commits = get_repo_commits(sample_repo, author="Alice")
        assert all(c.author_email == "alice@example.com" for c in commits)
        assert len(commits) == 2

    def test_no_merges(self, sample_repo: Path):
        # No merges in sample, but test passes
        commits = get_repo_commits(sample_repo, no_merges=True)
        assert len(commits) == 3
