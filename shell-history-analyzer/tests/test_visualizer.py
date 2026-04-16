import pytest
from pathlib import Path

from shell_history_analyzer.visualizer import export_json
from shell_history_analyzer.types import AnalysisResult


def test_export_json(tmp_path: Path):
    result = AnalysisResult(total_entries=100)
    p = tmp_path / "test.json"
    export_json(result, p)
    assert p.exists()
    data = p.read_text()
    assert '"total_entries": 100' in data
