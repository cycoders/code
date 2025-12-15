import io
from unittest.mock import patch

import pytest

from deadcode_hunter.issue import Issue
from deadcode_hunter.reporter import report


@pytest.fixture
def sample_issues():
    return [
        Issue("file.py", 5, 0, "mod", "unused_import", 90, "Unused"),
        Issue("file.py", 10, 0, "func", "unused_function", 80, "Unused"),
    ]


def test_report(sample_issues, capsys):
    report(sample_issues)
    captured = capsys.readouterr()
    assert "Deadcode Report" in captured.out
    assert "Total issues: 2" in captured.out


def test_empty_report(capsys):
    report([])
    captured = capsys.readouterr()
    assert captured.out == ""
