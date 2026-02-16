import pytest
from unittest.mock import patch
from web_vitals_cli.reporter import Reporter
from web_vitals_cli.types import PerfBudget


def test_terminal_report(sample_result):
    reporter = Reporter()
    with patch("rich.console.Console.print") as mock_print:
        reporter.terminal_report(sample_result, PerfBudget())
    mock_print.assert_called()


def test_html_report(tmp_path, sample_result):
    reporter = Reporter()
    html_path = tmp_path / "report.html"
    reporter.html_report(sample_result, None, html_path)
    assert html_path.exists()
    assert "Web Vitals" in html_path.read_text()