import ast
from pathlib import Path
from typing import List

class TimingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings: List[str] = []

    def visit_Compare(self, node):
        if any(isinstance(op, (ast.Eq, ast.NotEq)) for op in node.ops):
            if isinstance(node.left, (ast.Name, ast.Attribute)):
                self.findings.append(f"Potential timing leak at line {node.lineno}")
        self.generic_visit(node)


def scan_path(path: Path) -> List[str]:
    findings = []
    for pyfile in path.rglob("*.py"):
        try:
            tree = ast.parse(pyfile.read_text())
            v = TimingVisitor()
            v.visit(tree)
            findings.extend(v.findings)
        except Exception:
            pass
    return findings