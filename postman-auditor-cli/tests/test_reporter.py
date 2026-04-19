from postman_auditor_cli.issues import Issue
from postman_auditor_cli.reporter import Reporter
import io


def test_table_report(capsys):
    issues = [
        Issue("error", "test", "msg", ["path1"]),
        Issue("warning", "test2", "msg2", ["path2"]),
    ]
    Reporter.report(issues, "table")
    captured = capsys.readouterr()
    assert "ERROR" in captured.out
    assert "Errors: 1" in captured.out


def test_json_report():
    issues = [Issue("error", "e", "m", ["p"])]
    f = io.StringIO()
    Reporter.report(issues, "json", f)
    data = json.loads(f.getvalue())
    assert data["summary"]["error"] == 1
    assert len(data["issues"]) == 1
