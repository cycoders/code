from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

KNOWN_SIDE_EFFECTS = {"requests", "httpx", "socket", "subprocess", "os.environ"}

@dataclass
class SideEffect:
    module: str
    line: int
    kind: str
    detail: str


def find_side_effects(root: str | Path) -> list[SideEffect]:
    root = Path(root)
    results: list[SideEffect] = []
    for pyfile in root.rglob("*.py"):
        try:
            tree = ast.parse(pyfile.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    name = node.func.id
                else:
                    continue
                if name in {"get", "post", "connect", "Popen", "system"}:
                    results.append(
                        SideEffect(
                            module=str(pyfile.relative_to(root)),
                            line=node.lineno,
                            kind="network_or_subprocess",
                            detail=ast.unparse(node) if hasattr(ast, "unparse") else name,
                        )
                    )
    return results
