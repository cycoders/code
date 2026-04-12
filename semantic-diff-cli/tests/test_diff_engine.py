'''Tests for diff engine.''' 

import pytest
import tempfile
import os
from unittest.mock import MagicMock
from semantic_diff_cli.diff_engine import print_semantic_diff, normalize_content


class TestDiffEngine:
    @pytest.fixture
    def sample_files(self, tmp_path):
        old_file = tmp_path / "old.py"
        new_file = tmp_path / "new.py"
        old_file.write_text("def f(): pass")
        new_file.write_text("def f():pass")
        return old_file, new_file

    def test_no_semantic_change(self, mocker):
        mocker.patch("semantic_diff_cli.diff_engine.normalize_content", return_value="same\ncode")
        mock_console = mocker.patch("rich.console.Console")
        print_semantic_diff("test.py", "raw1", "raw2")
        mock_console().print.assert_called_with("[green]No semantic changes: test.py[/]")

    def test_git_diff_success(self, mocker):
        mocker.patch("semantic_diff_cli.diff_engine.normalize_content", side_effect=lambda f,c: c.replace("raw", "norm"))
        mock_git = mocker.patch("subprocess.run")
        mock_git.return_value.stdout = "colored diff"
        mock_console = mocker.patch("rich.console.Console")
        print_semantic_diff("test.py", "raw old", "raw new")
        mock_console().print.assert_any_call("colored diff", markup=False)

    def test_git_fallback(self, mocker):
        mocker.patch("semantic_diff_cli.diff_engine.normalize_content", return_value="diff1\n", new_callable=lambda: "diff2\n")
        mocker.patch("subprocess.run", side_effect=FileNotFoundError)
        mock_console = mocker.patch("rich.console.Console")
        print_semantic_diff("test.py", "a", "b")
        mock_console().print.assert_any_call("[yellow]git diff unavailable, using plain diff[/]")
