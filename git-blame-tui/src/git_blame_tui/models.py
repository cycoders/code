from dataclasses import dataclass, field
from typing import List, Optional

from datetime import datetime

@dataclass
class BlameEntry:
    lineno: int
    commit: str
    prev_commit: str
    author: str
    author_time: datetime
    summary: str
    content: str


@dataclass
class BlameBlock:
    commit: str
    prev_commit: str
    author: str
    author_time: datetime
    summary: str = ""
    lines: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.lines:
            self.line_count = len(self.lines)
        else:
            self.line_count = 0


BlameData = List[BlameEntry]