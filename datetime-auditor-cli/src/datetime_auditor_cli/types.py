from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class Issue:
    file: Path
    line: int
    column: int
    message: str
    severity: str = "warning"
    snippet: str | None = None

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}: {self.severity}: {self.message}"
