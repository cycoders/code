from enum import Enum
from dataclasses import dataclass
from typing import Literal
from sqlglot import exp


class Dialect(Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"


Severity = Literal["error", "warning", "info"]


@dataclass
class Issue:
    code: str
    severity: Severity
    message: str
    file: str
    line: int
    col: int

    def model_dump(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "col": self.col,
        }