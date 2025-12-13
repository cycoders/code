from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class GitFileChange:
    path: str
    insertions: int
    deletions: int

    def __post_init__(self):
        self.lines_changed = self.insertions + self.deletions


@dataclass
class GitCommit:
    sha: str
    timestamp: datetime
    author: str
    summary: str
    changes: List[GitFileChange] = field(default_factory=list)


@dataclass
class FileChurn:
    path: str
    total_churn: int = 0
    recent_churn: int = 0
    commit_count: int = 0
    last_commit: Optional[datetime] = None
    authors: Dict[str, int] = field(default_factory=dict)
    top_author: Optional[str] = None
    top_author_churn: int = 0
