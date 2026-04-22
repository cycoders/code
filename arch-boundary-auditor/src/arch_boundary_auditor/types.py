from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Violation:
    file: Path
    line: int
    from_layer: str
    to_layer: Optional[str]
    severity: str  # 'error' or 'warning'
    message: str