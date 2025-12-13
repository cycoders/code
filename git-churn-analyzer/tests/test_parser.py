from datetime import datetime

import pytest
from git_churn_analyzer.parser import parse_git_log
from git_churn_analyzer.models import GitCommit, GitFileChange


@pytest.mark.parametrize(
    "raw_output, expected_len",
    [
        ("", 0),
        ("invalid", 0),
        (
            "a1b2c3d4e5f6789012345678901234567890ab\t1640995200\tauthor1\tInitial",
            1,
        ),
    ],
)
def test_parse_git_log_empty(raw_output: str, expected_len: int):
    commits = parse_git_log(raw_output)
    assert len(commits) == expected_len


def test_parse_git_log_full(sample_git_output):
    commits = parse_git_log(sample_git_output)
    assert len(commits) == 2
    assert isinstance(commits[0], GitCommit)
    assert commits[0].sha == "a1b2c3d4e5f6789012345678901234567890ab"
    assert commits[0].author == "author1"
    dt = datetime.utcfromtimestamp(1640995200)
    assert commits[0].timestamp == dt
    assert len(commits[0].changes) == 2
    assert commits[0].changes[0].path == "file1.py"
    assert commits[0].changes[0].insertions == 10
    assert commits[0].changes[0].deletions == 2
    assert commits[0].changes[1].lines_changed == 5


def test_parse_binary_files():
    output = "sha...\t1234567890\tauth\tmsg\nfile.bin\t-\t-\n"
    commits = parse_git_log(output)
    assert len(commits) == 1
    change = commits[0].changes[0]
    assert change.path == "file.bin"
    assert change.insertions == 0
    assert change.deletions == 0
