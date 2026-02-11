from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class RepoInfo:
    path: str
    abs_path: str
    is_dirty: bool
    current_branch: str
    last_commit_date: datetime
    commit_count: int
    branch_count: int
    raw_git_size: int
    git_size: str  # Computed
    top_languages: List[str]
    remote_count: int
