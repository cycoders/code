import pytest
from test_impact_analyzer.analyzer import ImpactAnalyzer

def test_basic_analysis(tmp_path):
    cov = tmp_path / ".coverage"
    cov.write_text('{}')
    a = ImpactAnalyzer(str(cov))
    res = a.analyze("main", "HEAD")
    assert "changed_files" in res

def test_empty_diff():
    a = ImpactAnalyzer("/tmp/nonexistent")
    res = a.analyze("main", "main")
    assert res["recommended_tests"] == []