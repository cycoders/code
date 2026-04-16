import pytest
from collections import Counter

from shell_history_analyzer.analyzer import analyze_history
from shell_history_analyzer.types import HistoryEntry


def test_analyze_history(sample_zsh_entries):
    result = analyze_history(sample_zsh_entries)
    assert result.total_entries == 2
    assert result.total_commands == 2
    assert result.cmd_counter["git"] == 1
    assert result.cmd_counter["ls"] == 1
    assert result.productivity_score > 0
    assert len(result.repeated_lines) == 0  # no repeats


def test_repeated_detection():
    entries = [
        HistoryEntry(command="git status", full_line="git status", words=["git", "status"]),
    ] * 15
    result = analyze_history(entries)
    assert len(result.repeated_lines) == 1
    assert result.repeated_lines[0][1] == 15
