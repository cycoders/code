import ast
import sys
from typing import List, Dict, Any

class CognitiveComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.results: List[Dict[str, Any]] = []
        self.score: int = 0
        self.nesting: int = 0
        self.current_file: str = ""

    def visit_list(self, nodes: List[ast.AST]) -> None:
        """Visit a list of nodes, e.g., function body."""
        for node in nodes:
            self.visit(node)

    def increment(self, amount: int = 1) -> None:
        """Increment score by amount + current nesting."""
        self.score += amount + self.nesting

    def enter_structure(self) -> int:
        """Enter nested structure (increment nesting)."""
        self.nesting += 1
        return self.nesting - 1  # old value

    def exit_structure(self, old_nest: int) -> None:
        """Exit nested structure."""
        self.nesting = old_nest

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        score_start = self.score
        nesting_start = self.nesting
        self.score = 0
        self.nesting = 0
        self.visit_list(node.body)
        loc = (getattr(node, 'end_lineno', node.lineno) - node.lineno + 1)
        self.results.append({
            'file': self.current_file,
            'name': node.name,
            'lineno': node.lineno,
            'loc': loc,
            'complexity': self.score
        })
        self.score = score_start
        self.nesting = nesting_start

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        score_start = self.score
        nesting_start = self.nesting
        self.score = 0
        self.nesting = 0
        self.visit(node.body)
        loc = (getattr(node, 'end_lineno', node.lineno) - node.lineno + 1)
        self.results.append({
            'file': self.current_file,
            'name': '<lambda>',
            'lineno': node.lineno,
            'loc': loc,
            'complexity': self.score
        })
        self.score = score_start
        self.nesting = nesting_start

    def visit_If(self, node: ast.If) -> None:
        self.increment(1)
        old_nest = self.nesting
        self.generic_visit(node.test)
        self.nesting = old_nest + 1
        self.visit_list(node.body)
        self.nesting = old_nest
        if node.orelse:
            self.visit_list(node.orelse)

    def visit_For(self, node: ast.For) -> None:
        self.increment(1)
        old_nest = self.nesting
        self.generic_visit(node.iter)
        self.generic_visit([node.target])
        self.nesting = old_nest + 1
        self.visit_list(node.body)
        self.nesting = old_nest
        if node.orelse:
            self.visit_list(node.orelse)

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        self.increment(1)
        old_nest = self.nesting
        self.generic_visit(node.test)
        self.nesting = old_nest + 1
        self.visit_list(node.body)
        self.nesting = old_nest
        if node.orelse:
            self.visit_list(node.orelse)

    visit_AsyncWhile = visit_While

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.increment(1)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.increment(1)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.visit_list(node.body)
        for handler in node.handlers:
            self.visit(handler)
        self.visit_list(node.orelse)
        self.visit_list(getattr(node, 'finalbody', []))

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.increment(1)
        old_nest = self.nesting
        self.nesting = old_nest + 1
        if node.type:
            self.visit(node.type)
        if node.name:
            self.visit(node.name)
        self.visit_list(node.body)
        self.nesting = old_nest

    def visit_With(self, node: ast.With) -> None:
        self.increment(1)
        old_nest = self.nesting
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)
        self.nesting = old_nest + 1
        self.visit_list(node.body)
        self.nesting = old_nest

    visit_AsyncWith = visit_With

    if sys.version_info >= (3, 10):
        def visit_Match(self, node: ast.Match) -> None:
            self.increment(1)
            old_nest = self.nesting
            self.generic_visit(node.subject)
            self.nesting = old_nest + 1
            for case in node.cases:
                self.visit(case)
            self.nesting = old_nest

        def visit_MatchCase(self, node: 'ast.MatchCase') -> None:  # type: ignore
            self.increment(1)
            old_nest = self.nesting
            self.visit(node.pattern)
            if node.guard:
                self.visit(node.guard)
            self.visit_list(node.body)
            self.nesting = old_nest

    def generic_visit(self, node: ast.AST) -> None:
        """Fallback: visit children without increments."""
        super().generic_visit(node)


def compute_complexity(file_path: str) -> List[Dict[str, Any]]:
    """Compute complexity metrics for a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
        visitor = CognitiveComplexityVisitor()
        visitor.current_file = file_path
        visitor.visit(tree)
        return visitor.results
    except SyntaxError:
        return []
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return []