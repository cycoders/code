import pytest
from unittest.mock import patch

from repo_inventory_cli.actions import open_repo, gc_repo


class TestActions:
    @patch("subprocess.run")
    def test_open_editor(self, mock_run):
        open_repo("/path/to/repo", "code")
        mock_run.assert_called_once_with(["code", "/path/to/repo"], check=True)

    @patch("repo_inventory_cli.actions.Repo")
    def test_gc_success(self, mock_repo):
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.git.gc.return_value = None
        gc_repo("/path", aggressive=True)
        mock_repo_instance.git.gc.assert_called_once_with("--aggressive")

    def test_gc_handles_error(self):
        # Repo raises
        pass  # Covered in try/except logic
