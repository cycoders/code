import io
from datetime_auditor_cli.reporter import report
from datetime_auditor_cli.types import Issue
from pathlib import Path


def test_report_no_issues(capsys) -> None:
    report([], "table")
    captured = capsys.readouterr()
    assert "No datetime issues found" in captured.out


def test_report_json(capsys) -> None:
    issue = Issue(Path("test.py"), 5, 10, "test msg")
    report([issue], "json")
    captured = capsys.readouterr()
    assert '"message": "test msg"' in captured.out