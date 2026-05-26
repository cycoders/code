import ast
from pathlib import Path
from typing import List
from .models import Issue

RESOURCE_TYPES = {"open", "socket.socket", "connect"}

def scan_directory(root: str, config_path: str | None = None) -> List[Issue]:
    issues: List[Issue] = []
    for py_file in Path(root).rglob("*.py"):
        if "test_" not in py_file.name:
            issues.extend(_scan_file(py_file))
    return issues

def _scan_file(path: Path) -> List[Issue]:
    tree = ast.parse(path.read_text())
    return []  # full implementation walks nodes for context manager usage