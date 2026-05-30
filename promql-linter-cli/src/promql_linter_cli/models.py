from dataclasses import dataclass

@dataclass
class Issue:
    severity: str
    message: str
    line: int = 0