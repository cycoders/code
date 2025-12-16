from dataclasses import dataclass
from typing import Optional


@dataclass
class TodoItem:
    """Represents a single TODO/FIXME/HACK item."""
    filepath: str
    line: int
    tag: str
    message: str
    age_days: Optional[float] = None
    author: Optional[str] = None