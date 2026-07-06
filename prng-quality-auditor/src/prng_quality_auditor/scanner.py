import ast
from dataclasses import dataclass
from pathlib import Path

WEAK_CALLS = {"random", "randint", "choice", "shuffle", "seed"}

@dataclass
class Finding:
    path: str
    line: int
    message: str

def scan_path(root: str) -> list[Finding]:
    findings: list[Finding] = []
    for pyfile in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(pyfile.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in WEAK_CALLS:
                        findings.append(Finding(str(pyfile), node.lineno, "Weak RNG call detected"))
        except Exception:
            continue
    return findings