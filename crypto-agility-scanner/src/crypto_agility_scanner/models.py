from dataclasses import dataclass
from pathlib import Path

@dataclass
class Finding:
    file: Path
    line: int
    column: int
    algorithm: str
    severity: str
    suggestion: str
    confidence: float