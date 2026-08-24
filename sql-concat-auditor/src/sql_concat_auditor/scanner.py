import ast
from pathlib import Path
from typing import List

class SQLConcatVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("execute", "executemany"):
            for arg in node.args:
                if self._is_concat(arg):
                    self.findings.append({"line": node.lineno, "risk": "high"})
        self.generic_visit(node)

    def _is_concat(self, node):
        return isinstance(node, (ast.BinOp, ast.JoinedStr, ast.Call))

def scan_path(root: str) -> List[dict]:
    findings = []
    for py in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(py.read_text())
            v = SQLConcatVisitor()
            v.visit(tree)
            findings.extend(v.findings)
        except Exception:
            pass
    return findings