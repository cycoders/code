from collections import Counter, defaultdict
from datetime import datetime
from typing import List

import rich.progress
from rich import print as rprint

from .types import HistoryEntry, AnalysisResult


def analyze_history(entries: List[HistoryEntry]) -> AnalysisResult:
    """Analyze parsed history entries."""
    result = AnalysisResult(total_entries=len(entries))
    cmd_entries = [e for e in entries if e.words]
    result.total_commands = len(cmd_entries)

    # Command counter
    result.cmd_counter = dict(Counter(e.words[0] for e in cmd_entries))

    # Time spent (heuristic: assume 5-30s per cmd, avg based on length)
    for e in cmd_entries:
        est_time = min(30, max(5, len(e.full_line) / 10))
        result.time_spent_seconds += est_time

    # Daily trends
    result.daily_trends = dict(
        Counter(e.timestamp.strftime("%Y-%m-%d") for e in cmd_entries if e.timestamp)
    )

    # Repeated lines (>10x)
    line_counter = Counter(e.full_line.strip() for e in cmd_entries)
    result.repeated_lines = [(line, cnt) for line, cnt in line_counter.most_common() if cnt > 10]

    # Long unique commands
    cmd_freq = Counter(e.words[0] for e in cmd_entries)
    result.long_commands = [
        e for e in cmd_entries if len(e.full_line) > 80 and cmd_freq[e.words[0]] < 5
    ]

    # Productivity score (heuristic: % non-cd/ls/pwd + variety)
    productive_cmds = sum(cnt for cmd, cnt in result.cmd_counter.items() if cmd not in {"cd", "ls", "pwd"})
    result.productivity_score = min(100, (productive_cmds / max(1, result.total_commands)) * 100)

    return result
