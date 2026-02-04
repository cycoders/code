from git_history_viz.parser import parse_repo


class TestParser:
    def test_parse_sample_repo(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 10)
        assert len(commits) == 4
        assert all(node.sha in commits for node in commits.values())

    def test_refs_filter(self, sample_repo):
        commits = parse_repo(str(sample_repo), ["main"], 10)
        assert len(commits) == 4  # includes history

    def test_max_commits_limits(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 2)
        assert len(commits) == 2

    def test_empty_repo(self, tmp_path):
        repo_path = tmp_path / "empty"
        Repo.init(repo_path)
        commits = parse_repo(str(repo_path), None, 10)
        assert commits == {}

    def test_invalid_path(self):
        from pathlib import Path
        import os
        p = Path("/nonexistent")
        from pytest import raises
        with raises(ValueError, match="Invalid Git repository"):
            parse_repo(str(p), None, 10)
