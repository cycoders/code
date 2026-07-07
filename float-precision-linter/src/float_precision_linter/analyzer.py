import ast
from pathlib import Path
from typing import List, Dict

PATTERNS = ["sum", "mean", "==", "!="]

def analyze_path(path: str, tol: float) -> List[Dict]:
    issues = []
    for pyfile in Path(path).rglob("*.py"):
        tree = ast.parse(pyfile.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) in PATTERNS:
                issues.append({"file": str(pyfile), "line": node.lineno, "suggestion": "use math.fsum or numpy.isclose"})
    return issues