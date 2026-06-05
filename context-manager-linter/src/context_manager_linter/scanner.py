import ast
from pathlib import Path
from typing import List
KNOWN_RESOURCES = {"open", "Lock", "RLock", "Semaphore", "Session", "connect"}

def scan_directory(root: str, config_path: str | None = None) -> List[str]:
    findings: List[str] = []
    for py in Path(root).rglob("*.py"):
        if "test_" in py.name or "__pycache__" in str(py):
            continue
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in KNOWN_RESOURCES:
                    findings.append(f"{py}:{node.lineno} - bare {node.func.id}()")
    return findings