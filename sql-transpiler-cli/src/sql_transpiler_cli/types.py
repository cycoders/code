from dataclasses import dataclass
from typing import Optional


@dataclass
class Issue:
    """Represents a transpilation or validation issue."""

    type: str  # 'parse_from', 'compile_to', 'parse_to'
    message: str
    line: Optional[int] = None