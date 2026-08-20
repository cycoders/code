from dataclasses import dataclass
from typing import Callable

@dataclass
class Violation:
    line: int
    message: str
    fix: str | None = None

Rule = Callable[[list], list[Violation]]

def duplicate_keys(entries) -> list[Violation]:
    seen = {}
    violations = []
    for e in entries:
        if e.key in seen:
            violations.append(Violation(e.line, f"Duplicate key '{e.key}'", None))
        seen[e.key] = e.line
    return violations