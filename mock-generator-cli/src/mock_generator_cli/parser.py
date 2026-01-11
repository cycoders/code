import ast
from typing import Set, Dict, Optional, Any
from pathlib import Path


class ImportResolver(ast.NodeVisitor):
    """Resolves import aliases to full module/function paths and tracks local definitions."""

    def __init__(self) -> None:
        self.import_map: Dict[str, str] = {}
        self.local_defs: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            name = alias.name.split(".")[0]
            local_name = alias.asname or name
            self.import_map[local_name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        module_name = node.module or ""
        for alias in node.names:
            local_name = alias.asname or alias.name
            full_name = f"{module_name}.{alias.name}" if module_name else alias.name
            self.import_map[local_name] = full_name
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.local_defs.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.local_defs.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.local_defs.add(node.name)
        self.generic_visit(node)

    def resolve_target(self, target: str) -> Optional[str]:
        """Resolve aliased names to full dotted paths."""
        parts = target.split(".")
        first_part = parts[0]
        if first_part in self.import_map:
            resolved = self.import_map[first_part]
            if len(parts) > 1:
                resolved += "." + ".".join(parts[1:])
            return resolved
        return target


class CallExtractor(ast.NodeVisitor):
    """Extracts external call targets from AST subtree."""

    def __init__(self, resolver: ImportResolver) -> None:
        self.resolver = resolver
        self.external_calls: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> Any:
        raw_target = self._extract_func_target(node.func)
        if raw_target:
            resolved = self.resolver.resolve_target(raw_target)
            if resolved and self._is_external(resolved):
                self.external_calls.add(resolved)
        self.generic_visit(node)

    def _extract_func_target(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base_target = self._extract_func_target(node.value)
            if base_target:
                return f"{base_target}.{node.attr}"
        return None

    def _is_external(self, target: str) -> bool:
        first_part = target.split(".")[0]
        if target.startswith(("self.", "cls.", "builtins.")) or first_part in ("len", "str", "list"):
            return False
        return first_part not in self.resolver.local_defs


def find_function(parent: ast.AST, name: str) -> Optional[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Find FunctionDef or AsyncFunctionDef by name in parent AST node."""
    class Finder(ast.NodeVisitor):
        def __init__(self, target: str):
            self.target = target
            self.found: Optional[ast.FunctionDef | ast.AsyncFunctionDef] = None

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.name == self.target:
                self.found = node
            else:
                self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            if node.name == self.target:
                self.found = node
            else:
                self.generic_visit(node)

    finder = Finder(name)
    finder.visit(parent)
    return finder.found


def find_class(parent: ast.AST, name: str) -> Optional[ast.ClassDef]:
    """Find ClassDef by name in parent AST node."""
    class Finder(ast.NodeVisitor):
        def __init__(self, target: str):
            self.target = target
            self.found: Optional[ast.ClassDef] = None

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            if node.name == self.target:
                self.found = node
            else:
                self.generic_visit(node)

    finder = Finder(name)
    finder.visit(parent)
    return finder.found