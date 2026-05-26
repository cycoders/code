import ast
from pathlib import Path
from typing import List
from .rules import BLOCKING_CALLS

class BlockingVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKING_CALLS:
            self.issues.append((node.lineno, node.func.attr))
        self.generic_visit(node)

def detect_blocks(paths: List[str]):
    issues = []
    for p in paths:
        for file in Path(p).rglob("*.py"):
            tree = ast.parse(file.read_text())
            v = BlockingVisitor()
            v.visit(tree)
            for lineno, name in v.issues:
                issues.append(f"{file}:{lineno} blocking call: {name}")
    return issues