import libcst as cst
from pathlib import Path
from typing import List, Dict

class LockGraphVisitor(cst.CSTVisitor):
    def __init__(self):
        self.locks: Dict[str, List[str]] = {}
        self.current_func = "global"

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.current_func = node.name.value

    def visit_Call(self, node: cst.Call) -> None:
        if isinstance(node.func, cst.Attribute) and node.func.attr.value in ("acquire", "__aenter__"):
            lock_name = node.func.value.value if hasattr(node.func.value, "value") else "unknown"
            self.locks.setdefault(lock_name, []).append(self.current_func)

def analyze_path(path: str, threshold: str = "medium") -> List[Dict]:
    results = []
    for py_file in Path(path).rglob("*.py"):
        try:
            tree = cst.parse_module(py_file.read_text())
            visitor = LockGraphVisitor()
            tree.walk(visitor)
            if visitor.locks:
                results.append({"file": str(py_file), "locks": visitor.locks})
        except Exception:
            continue
    return results