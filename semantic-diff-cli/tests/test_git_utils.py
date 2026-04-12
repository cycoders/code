'''Tests for git utils.''' 

import pytest
from unittest.mock import MagicMock
from semantic_diff_cli.git_utils import perform_git_semdiff, is_likely_binary


class TestGitUtils:
    def test_is_binary(self):
        assert is_likely_binary("img.png")
        assert not is_likely_binary("code.py")

    def test_perform_git_semdiff(self, mocker):
        mock_repo = MagicMock()
        mock_repo.git.diff.return_value = "file1.py\nfile2.js"
        mock_repo.git.show.side_effect = ["content1", "content2", "content3", "content4"]
        mocker.patch("git.Repo", return_value=mock_repo)
        mock_print_diff = mocker.patch("semantic_diff_cli.git_utils.print_semantic_diff")
        mock_console = mocker.patch("rich.console.Console")

        perform_git_semdiff("base", "head", Path("."))

        assert mock_print_diff.call_count == 2
        mock_console().print.assert_any_call("[bold green]Analyzing 2 files...[/]")
