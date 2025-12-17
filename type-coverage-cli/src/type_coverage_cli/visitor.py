import ast
from typing import Optional

from .models import ElementCoverage

class LocalStats:
    def __init__(self) -> None:
        self.funcs = ElementCoverage()
        self.params = ElementCoverage()
        self.returns = ElementCoverage()

    def to_file_stats(self, path: str) -> "FileStats":
        from .models import FileStats
        return FileStats(path, self.funcs, self.params, self.returns)

class CoverageVisitor(ast.NodeVisitor):
    """AST visitor to collect type coverage stats."""

    def __init__(self) -> None:
        self.stats: LocalStats = LocalStats()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Visit methods
        for stmt in node.body:
            self.visit(stmt)
        self.generic_visit(node)

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.stats.funcs.total += 1

        # Positional args only
        pos_args = node.args.args
        total_params = len(pos_args)
        typed_params = sum(1 for arg in pos_args if arg.annotation is not None)
        self.stats.params.total += total_params
        self.stats.params.typed += typed_params

        has_return_ann = node.returns is not None
        self.stats.returns.total += 1
        self.stats.returns.typed += 1 if has_return_ann else 0

        # Func fully typed: all pos args + return
        all_params_typed = all(arg.annotation is not None for arg in pos_args)
        if all_params_typed and has_return_ann:
            self.stats.funcs.typed += 1
