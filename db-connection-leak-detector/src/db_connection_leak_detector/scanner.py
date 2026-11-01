import libcst as cst
from pathlib import Path
from typing import List

class ConnectionVisitor(cst.CSTVisitor):
    def __init__(self):
        self.findings: List[str] = []

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Attribute) and node.func.attr.value in {"connect", "cursor"}:
            self.findings.append(f"Potential leak at line {node.lineno}")

def scan_path(path: str) -> List[str]:
    findings = []
    for py_file in Path(path).rglob("*.py"):
        try:
            tree = cst.parse_module(py_file.read_text())
            visitor = ConnectionVisitor()
            tree.walk(visitor)
            findings.extend(visitor.findings)
        except Exception:
            continue
    return findings