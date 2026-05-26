from dataclasses import dataclass

@dataclass
class Issue:
    file: str
    line: int
    severity: str
    message: str
    suggestion: str