import ast
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from .patterns import Pattern

def find_matches(path: Path, pattern: Pattern):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    matches = []
    for node in ast.walk(tree):
        if pattern.matches(node):
            matches.append((path, node.lineno))
    return matches