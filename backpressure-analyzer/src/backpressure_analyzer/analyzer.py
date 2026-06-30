import ast
from pathlib import Path
from typing import List

class Finding:
    def __init__(self, file: str, line: int, msg: str):
        self.file = file
        self.line = line
        self.msg = msg
    def __str__(self):
        return f"{self.file}:{self.line} {self.msg}"

def analyze_path(root: str, metrics_path: str | None = None) -> List[Finding]:
    findings: List[Finding] = []
    for py in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(py.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("Queue", "create_task"):
                    findings.append(Finding(str(py), node.lineno, "potential unbounded producer"))
    return findings