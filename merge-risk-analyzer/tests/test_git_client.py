import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from merge_risk_analyzer.git_client import GitClient


def test_get_change_stats_empty(tmp_path, mock_git_repo):
    mock_repo = mock_git_repo
    mock_repo.git.diff.return_value = ""
    with patch("git.Repo", return_value=mock_repo):
        gc = GitClient(tmp_path)
        ins, del_ = gc.get_change_stats("base", "head", "file.py")
        assert ins == 0
        assert del_ == 0


def test_get_change_stats_valid(tmp_path, mock_git_repo):
    mock_repo = mock_git_repo
    mock_repo.git.diff.return_value = "50\t20\tfile.py"
    with patch("git.Repo", return_value=mock_repo):
        gc = GitClient(tmp_path)
        ins, del_ = gc.get_change_stats("base", "head", "file.py")
        assert ins == 50
        assert del_ == 20


def test_get_historical_merge_touches(tmp_path, mock_git_repo):
    mock_repo = mock_git_repo
    mock_repo.git.log.return_value = "commit1\ncommit2"
    with patch("git.Repo", return_value=mock_repo):
        gc = GitClient(tmp_path)
        count = gc.get_historical_merge_touches("file.py")
        assert count == 2


def test_changed_files(tmp_path, mock_git_repo):
    mock_repo = mock_git_repo
    mock_repo.git.diff.return_value = "file1.py\nfile2.py"
    with patch("git.Repo", return_value=mock_repo):
        gc = GitClient(tmp_path)
        files = gc.get_changed_files("base", "head")
        assert files == {"file1.py", "file2.py"}


def test_no_git_repo(tmp_path):
    with pytest.raises(ValueError, match="Not a Git repository"):
        GitClient(tmp_path)
