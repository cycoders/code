from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class HistoryEntry:
    """Represents a single entry from shell history."""
    timestamp: Optional[datetime] = None
    command: str = ""
    full_line: str = ""
    words: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Results from analyzing history entries."""
    total_entries: int = 0
    total_commands: int = 0
    cmd_counter: dict[str, int] = field(default_factory=dict)
    time_spent_seconds: float = 0.0
    daily_trends: dict[str, int] = field(default_factory=dict)
    repeated_lines: list[tuple[str, int]] = field(default_factory=list)
    long_commands: list[HistoryEntry] = field(default_factory=list)
    productivity_score: float = 0.0  # 0-100 heuristic
