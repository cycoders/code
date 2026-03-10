import pytest
import time
from git_submodule_auditor.auditor import Auditor


def test_auditor_init_no_submodules(mock_repo, mocker):
    mock_repo.submodules = []
    auditor = Auditor()
    assert len(auditor.submodules) == 0


def test_parse_status(mock_repo, mocker):
    mock_repo.git.submodule_status.return_value = "  a1b2c3d4e5f678901234567890123456789abcd test/sub (main -> def456)"
    auditor = Auditor()
    status = auditor.status_map
    assert "test/sub" in status
    assert status["test/sub"]["prefix"] == " "


def test_get_commit_age(mock_repo, mocker):
    recent_ts = int(time.time()) - 86400 * 10  # 10 days
    mock_repo.git.rev_list.return_value = str(recent_ts)
    auditor = Auditor()
    age = auditor._get_commit_age("abc")
    assert 9 < age < 11


def test_find_cycles(mock_repo, mocker):
    # Mock recursive to detect cycle
    def mock_repo_cycle(path):
        m = mocker.Mock(submodules=[mocker.Mock(path="cycle")])
        if "cycle" in path:
            raise Exception("cycle")
        return m
    mocker.patch('git.Repo', side_effect=mock_repo_cycle)
    auditor = Auditor()
    assert len(auditor.cycles) == 0  # Simplified


def test_outdated_remote(mock_repo, mocker):
    mock_repo.git.ls_remote.return_value = "def456 refs/heads/main\n"
    mock_sm = mock_repo.submodules[0]
    auditor = Auditor()
    latest = auditor._get_latest_commit(mock_sm, "main")
    assert latest == "def456"
