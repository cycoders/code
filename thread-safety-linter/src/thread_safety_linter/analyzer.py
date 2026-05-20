import ast
from pathlib import Path
from typing import List

class Issue:
    def __init__(self, file, line, message, severity="medium"):
        self.file = file
        self.line = line
        self.message = message
        self.severity = severity
    def __str__(self):
        return f"{self.file}:{self.line} [{self.severity}] {self.message}"

def analyze_path(root: str) -> List[Issue]:
    issues = []
    for py_file in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text())
            # Placeholder for real analysis passes
            if "threading" in py_file.read_text():
                issues.append(Issue(str(py_file), 1, "Consider reviewing lock usage"))
        except Exception:
            pass
    return issues
