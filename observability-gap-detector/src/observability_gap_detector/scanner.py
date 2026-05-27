import libcst as cst
from pathlib import Path
from typing import List

class ObservabilityVisitor(cst.CSTVisitor):
    def __init__(self):
        self.gaps: List[str] = []

    def visit_FunctionDef(self, node):
        if not any(d.value.value.startswith("@otel") for d in node.decorators):
            self.gaps.append(f"Missing tracing: {node.name.value}")

def scan_codebase(root: str) -> List[str]:
    gaps = []
    for py in Path(root).rglob("*.py"):
        tree = cst.parse_module(py.read_text())
        v = ObservabilityVisitor()
        tree.walk(v)
        gaps.extend(v.gaps)
    return gaps