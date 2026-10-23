import ast
from pathlib import Path
from typing import List

def analyze_path(path: str, enable_trace: bool = False, duration: float = 0.0) -> List[str]:
    results: List[str] = []
    for py_file in Path(path).rglob("*.py"):
        with open(py_file) as f:
            tree = ast.parse(f.read(), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "create_task":
                results.append(f"Potential leak at {py_file}:{node.lineno}")
    if enable_trace:
        results.append("Runtime tracing not enabled in this build")
    return results