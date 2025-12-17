import pytest
from rich.console import Console
from link_auditor.reporter import report_results


def test_report_table(capsys):
    results = [
        {"url": "https://ok", "status_code": 200},
        {"url": "https://fail", "status_code": 404, "error": None},
    ]
    console = Console(force_terminal=True)
    report_results(results, "table", None, console)
    captured = capsys.readouterr()
    assert "✓ 1 working" in captured.out
    assert "✗ 1 broken" in captured.out


def test_export_json(tmp_path):
    output = tmp_path / "report.json"
    results = [{"url": "test"}]
    report_results(results, "table", str(output), Console())
    assert output.exists()
