from __future__ import annotations
import ast
from typing import List, Set
from .rules import TAINT_SOURCES, TAINT_SINKS

class TaintAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[dict] = []
        self.tainted: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in TAINT_SINKS:
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.tainted:
                    self.issues.append({"line": node.lineno, "sink": node.func.attr})
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', None) in TAINT_SOURCES:
                    self.tainted.add(target.id)
        self.generic_visit(node)