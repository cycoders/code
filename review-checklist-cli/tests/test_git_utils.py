import pytest
from review_checklist_cli.git_utils import get_changed_files, is_git_repo


def test_is_git_repo(mock_subprocess):  # from conftest
    assert is_git_repo() is True


def test_get_changed_files(mock_subprocess):
    changes = get_changed_files("main", "HEAD")
    assert len(changes) == 3
    assert changes[0] == ("src/main.py", "M")
    assert changes[1] == ("docker/Dockerfile", "A")
    assert changes[2] == ("tests/old_test.py", "D")


def test_get_changed_files_no_changes(mock_subprocess, monkeypatch):
    def mock_stdout(cmd):
        return MagicMock(stdout="", returncode=0)
    monkeypatch.setattr("subprocess.run", mock_stdout)
    assert get_changed_files("main", "HEAD") == []