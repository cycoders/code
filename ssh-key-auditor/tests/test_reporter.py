import io
from ssh_key_auditor.reporter import report
from ssh_key_auditor.models import Issue, KeyInfo, Severity


def test_report_json(capsys):
    issues = [
        Issue("test.pub", 1, KeyInfo("rsa", 1024, None, "fp", "com"), "WEAK", "msg", Severity.CRITICAL)
    ]
    report(issues, "json")
    captured = capsys.readouterr()
    assert '"severity": "CRITICAL"' in captured.out


def test_no_issues(capsys):
    report([], "table")
    captured = capsys.readouterr()
    assert "No issues found" in captured.out