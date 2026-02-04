from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CommitNode:
    """
    Immutable Git commit representation.
    """
    sha: str  # full SHA
    short_sha: str  # abbreviated
    message: str
    author: str
    date: str
    parents: List[str]  # full SHA list
