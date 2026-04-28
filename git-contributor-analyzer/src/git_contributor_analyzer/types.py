from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class CommitInfo:
    hash: str
    author_name: str
    author_email: str
    authored_date: datetime
    insertions: int
    deletions: int
    files_changed: int


@dataclass
class ContributorStats:
    email: str
    name: str
    commit_count: int
    total_insertions: int
    total_deletions: int
    net_loc: int
    first_contrib: datetime
    last_contrib: datetime
    active_days: int
    max_streak: int
    avg_insertions_per_commit: float

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["first_contrib"] = self.first_contrib.isoformat()
        d["last_contrib"] = self.last_contrib.isoformat()
        return d
