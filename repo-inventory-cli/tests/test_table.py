import pytest
from unittest.mock import Mock

from repo_inventory_cli.table import render_table, console
from repo_inventory_cli.models import RepoInfo


class TestTable:
    @pytest.fixture
    def mock_repos(self):
        return [Mock(spec=RepoInfo, path="test/repo", is_dirty=False, commit_count=5)]

    def test_empty(self, mock_repos):
        render_table([])
        assert "No repositories" in console.out_stream.getvalue()

    def test_renders(self, mock_repos):
        mock_repos[0].is_dirty = False
        render_table(mock_repos)
        output = console.out_stream.getvalue()
        assert "Local Git Repositories" in output
        assert "🟢" in output
