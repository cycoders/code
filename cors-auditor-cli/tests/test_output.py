from cors_auditor_cli.output import render_console, render_json
from cors_auditor_cli.models import AuditReport, CheckResult


def test_render_json(capsys):
    report = AuditReport(
        url="https://test.com",
        checks=[CheckResult(type="simple", origin="loc", status_code=200, passed=True, details=["ok"])],
    )
    render_json(report)
    captured = capsys.readouterr()
    assert '"passed": true' in captured.out

# Note: Console rendering hard to unit test fully; integration via CLI tests