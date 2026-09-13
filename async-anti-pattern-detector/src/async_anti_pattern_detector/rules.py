from dataclasses import dataclass

@dataclass
class Finding:
    line: int
    col: int
    rule: str
    severity: str
    message: str
    suggestion: str

RULES = ["BLOCKING_CALL", "TASK_LEAK", "GATHER_NO_RETURN_EXCEPTIONS"]