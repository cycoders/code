import libcst as cst
from pathlib import Path
from typing import List

KNOWN_LIBRARIES = {"httpx", "aiohttp", "celery", "rq"}

class CorrelationVisitor(cst.CSTVisitor):
    def __init__(self):
        self.issues: List[str] = []

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Attribute):
            if node.func.attr.value in {"post", "get", "send", "delay"}:
                self.issues.append(f"Potential missing correlation ID at {node.func.attr.value}")

def scan_repository(root: str) -> List[str]:
    issues: List[str] = []
    for py_file in Path(root).rglob("*.py"):
        try:
            tree = cst.parse_module(py_file.read_text())
            visitor = CorrelationVisitor()
            tree.walk(visitor)
            issues.extend(visitor.issues)
        except Exception:
            continue
    return issues