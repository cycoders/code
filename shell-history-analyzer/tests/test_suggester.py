import pytest

from shell_history_analyzer.suggester import suggest_optimizations
from shell_history_analyzer.types import AnalysisResult, HistoryEntry


def test_suggest_optimizations():
    result = AnalysisResult(
        repeated_lines=[("git log --oneline --graph --all", 20)],
        long_commands=[HistoryEntry(full_line="very long cmd" * 10, words=["long"])],
    )
    sugs = suggest_optimizations(result)
    assert len(sugs) > 0
    assert "alias" in sugs[0]
