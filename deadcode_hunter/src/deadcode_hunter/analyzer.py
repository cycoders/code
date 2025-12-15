import ast
from pathlib import Path
from typing import List

from .issue import Issue


class ModuleLevelVisitor(ast.NodeVisitor):
    """AST visitor for module-level defs, assigns, loads. Ignores nested scopes."""

    def __init__(self) -> None:
        self.in_nested = False
        self.defs: set[str] = set()
        self.global_assigned: set[str] = set()
        self.loads: set[str] = set()
        self.potential_defs: list[tuple[str, int, int]] = []
        self.potential_vars: list[tuple[str, int, int]] = []

    def _enter_nested(self, node: ast.AST) -> None:
        was_nested = self.in_nested
        self.in_nested = True
        self.generic_visit(node)
        self.in_nested = was_nested

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not self.in_nested:
            self.defs.add(node.name)
            self.potential_defs.append((node.name, node.lineno, node.col_offset))
        self._enter_nested(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # Same logic

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not self.in_nested:
            self.defs.add(node.name)
            self.potential_defs.append((node.name, node.lineno, node.col_offset))
        self._enter_nested(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._enter_nested(node)

    def visit_Name(self, node: ast.Name) -> None:
        if not self.in_nested and isinstance(node.ctx, ast.Load):
            self.loads.add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self.in_nested:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.global_assigned.add(target.id)
                    self.potential_vars.append((target.id, node.lineno, node.col_offset))
        self.generic_visit(node)


class ImportVisitor(ModuleLevelVisitor):
    """AST visitor for module-level imports (non-star)."""

    def __init__(self) -> None:
        super().__init__()
        self.potential_imports: list[tuple[str, int, int]] = []
        self.import_names: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        if not self.in_nested:
            for alias in node.names:
                imp_name = alias.asname or alias.name.split(".")[0]
                self.import_names.add(imp_name)
                self.potential_imports.append((imp_name, node.lineno, node.col_offset))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not self.in_nested and (not node.names or node.names[0].name != "*"):
            for alias in node.names:
                imp_name = alias.asname or alias.name
                self.import_names.add(imp_name)
                self.potential_imports.append((imp_name, node.lineno, node.col_offset))
        self.generic_visit(node)


def analyze_file(file_path: Path) -> List[Issue]:
    """Analyze a single Python file for deadcode."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []  # Gracefully skip broken syntax
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    imp_visitor = ImportVisitor()
    imp_visitor.visit(tree)

    mod_visitor = ModuleLevelVisitor()
    mod_visitor.visit(tree)

    issues: List[Issue] = []

    # Unused imports
    for name, line, col in imp_visitor.potential_imports:
        if name not in mod_visitor.loads:
            issues.append(
                Issue(
                    str(file_path),
                    line,
                    col,
                    name,
                    "unused_import",
                    90,
                    "Unused import",
                )
            )

    # Unused defs (funcs/classes)
    for name, line, col in mod_visitor.potential_defs:
        if name not in mod_visitor.loads:
            issues.append(
                Issue(
                    str(file_path),
                    line,
                    col,
                    name,
                    "unused_function" if "def" else "unused_class",  # Approx
                    80,
                    "Unused definition",
                )
            )

    # Unused global vars
    for name, line, col in mod_visitor.potential_vars:
        if name not in mod_visitor.loads:
            issues.append(
                Issue(
                    str(file_path),
                    line,
                    col,
                    name,
                    "unused_variable",
                    70,
                    "Potentially unused global variable",
                )
            )

    return issues
