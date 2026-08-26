import pytest
from memfrag_profiler.analyzer import analyze

def test_analyze_runs():
    result = analyze(1, 0.1)
    assert "samples" in result

def test_score_range():
    result = analyze(1, 0.1)
    assert 0 <= result["fragmentation_score"] <= 10

def test_empty_duration():
    result = analyze(1, 0)
    assert len(result["samples"]) == 0