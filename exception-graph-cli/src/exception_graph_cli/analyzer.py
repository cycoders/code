from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator


def find_python_files(root: Path, exclude: set[str]) -> Iterator[Path]:
    for p in root.rglob("*.py"):
        if any(part in exclude for part in p.parts):
            continue
        yield p


def extract_exceptions(tree: ast.AST) -> set[str]:
    excs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc:
            if isinstance(node.exc, ast.Name):
                excs.add(node.exc.id)
            elif isinstance(node.exc, ast.Attribute):
                excs.add(node.exc.attr)
    return excs