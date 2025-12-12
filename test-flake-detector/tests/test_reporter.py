import json
import pytest
from pathlib import Path

from test_flake_detector.reporter import report_json, report_html


SAMPLE_STATS = [
    {"nodeid": "test.py::test_flaky", "flake_rate": 0.3, "passes": 7, "fails": 3}
]


def test_report_json(tmp_path: Path) -> None:
    json_file = tmp_path / "stats.json"
    report_json(SAMPLE_STATS, json_file)
    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert data[0]["flake_rate"] == 0.3


def test_report_html(tmp_path: Path) -> None:
    html_file = tmp_path / "report.html"
    report_html(SAMPLE_STATS, 0.1, html_file)
    assert html_file.exists()
    html = html_file.read_text()
    assert "test_flaky" in html
    assert "30.0%" in html
    assert 'class="flaky"' in html