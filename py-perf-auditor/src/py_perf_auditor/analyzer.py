import ast
import os
import typing as t
from collections import namedtuple
from pathlib import Path

from rich.console import Console

console = Console()


Violation = namedtuple(
    "Violation",
    [
        "lineno",
        "col_offset",
        "rule",
        "severity",
        "message",
        "suggestion",
    ],
)


class PerfVisitor(ast.NodeVisitor):
    """AST visitor detecting perf pitfalls."""

    def __init__(self) -> None:
        self.violations: list[Violation] = []

    @staticmethod
    def _likely_str(node: ast.AST) -> bool:
        """Heuristic: node likely evaluates to str."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        if isinstance(node, ast.Name):
            return True  # heuristic: common var names imply str
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return (
                PerfVisitor._likely_str(node.left)
                or PerfVisitor._likely_str(node.right)
            )
        return False

    @staticmethod
    def _likely_list(node: ast.AST) -> bool:
        """Heuristic: node likely evaluates to list."""
        if isinstance(node, (ast.List, ast.ListComp)):
            return True
        if isinstance(node, ast.Call) and node.func.id == "list":
            return True
        return False

    def visit_For(self, node: ast.AST) -> None:
        self._check_loop_body(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AST) -> None:
        self._check_loop_body(node)
        self.generic_visit(node)

    def visit_While(self, node: ast.AST) -> None:
        self._check_loop_body(node)
        self.generic_visit(node)

    def _check_loop_body(self, loop_node: ast.AST) -> None:
        """Check for pitfalls inside loop body."""
        for child in ast.walk(loop_node):
            self._check_string_concat(child)
            self._check_list_concat(child)
            self._check_list_on_map_filter(child)
            self._check_list_dict_keys(child)

    def _check_string_concat(self, node: ast.AST) -> None:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            if self._likely_str(node.left) and self._likely_str(node.right):
                self.violations.append(
                    Violation(
                        node.lineno,
                        getattr(node, "col_offset", 0),
                        "string-concat-loop",
                        "HIGH",
                        "String concatenation in loop (quadratic time)",
                        "Use `''.join(parts)` for 10x+ speedup",
                    )
                )

    def _check_list_concat(self, node: ast.AST) -> None:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            if self._likely_list(node.left) and self._likely_list(node.right):
                self.violations.append(
                    Violation(
                        node.lineno,
                        getattr(node, "col_offset", 0),
                        "list-concat",
                        "MED",
                        "List concatenation creates new lists",
                        "Use `list1.extend(list2)` for 2-5x speedup",
                    )
                )

    def _check_list_on_map_filter(self, node: ast.AST) -> None:
        if (
            isinstance(node, ast.Call)
            and node.func is not None
            and node.func.id == "list"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Call)
            and node.args[0].func is not None
            and node.args[0].func.id in ("map", "filter")
        ):
            self.violations.append(
                Violation(
                    node.lineno,
                    getattr(node, "col_offset", 0),
                    "list-on-map-filter",
                    "MED",
                    "`list(map/filter)` materializes full list early",
                    "Use generator `(f(x) for x in ...)` to save 50%+ memory",
                )
            )

    def _check_list_dict_keys(self, node: ast.AST) -> None:
        if (
            isinstance(node, ast.Call)
            and node.func is not None
            and node.func.id == "list"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Attribute)
            and node.args[0].attr == "keys"
        ):
            self.violations.append(
                Violation(
                    node.lineno,
                    getattr(node, "col_offset", 0),
                    "list-dict-keys",
                    "LOW",
                    "`list(d.keys())` unnecessary",
                    "Iterate directly `for k in d:`",
                )
            )


def analyze_file(file_path: Path) -> list[Violation]:
    """Analyze single Python file."""
    if not file_path.is_file() or file_path.suffix != ".py":
        return []

    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    visitor = PerfVisitor()
    visitor.visit(tree)
    return visitor.violations


def analyze_directory(
    dir_path: Path,
    ignore_dirs: list[str] = None,
    verbose: bool = False,
) -> dict[Path, list[Violation]]:
    """Analyze all .py files in directory recursively."""
    if ignore_dirs is None:
        ignore_dirs = {
            ".git",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
        }

    violations: dict[Path, list[Violation]] = {}
    py_files = []

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        py_files.extend(Path(root) / f for f in files if f.endswith(".py"))

    for py_file in py_files:
        file_violations = analyze_file(py_file)
        if file_violations:
            violations[py_file] = file_violations
        if verbose and file_violations:
            console.print(f"[yellow]{py_file}: {len(file_violations)} issues[/yellow]")

    return violations