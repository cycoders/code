import pytest

from repo_inventory_cli.stats import compute_repo_stats
from repo_inventory_cli.models import RepoInfo


class TestStats:
    def test_basic_stats(self, sample_repo: Path):
        import git
        repo = git.Repo(sample_repo)
        info = compute_repo_stats(repo, sample_repo)
        assert isinstance(info, RepoInfo)
        assert info.commit_count == 1
        assert info.branch_count >= 1
        assert info.top_languages  # At least .py, .md
        assert info.remote_count == 0

    def test_dirty_status(self, dirty_repo: Path):
        repo = Repo(dirty_repo)
        info = compute_repo_stats(repo, dirty_repo)
        assert info.is_dirty is True

    def test_orphaned(self, orphaned_repo: Path):
        repo = Repo(orphaned_repo)
        info = compute_repo_stats(repo, orphaned_repo)
        assert info.remote_count == 0

    def test_size_zero(self, sample_repo: Path):
        info = compute_repo_stats(Repo(sample_repo), sample_repo)
        assert info.raw_git_size >= 0
