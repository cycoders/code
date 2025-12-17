import ast
from typing import Set


class ImportFinder(ast.NodeVisitor):
    """AST visitor to extract and resolve imported modules to absolute dotted names."""

    def __init__(self, importer_module: str):
        self.importer_parts = importer_module.split(".")
        self.imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.module != "__future__":
            resolved = self._resolve_module(node.module, node.level)
            self._add(resolved)
        self.generic_visit(node)

    def _resolve_module(self, module_str: str, level: int) -> str:
        parts = module_str.split(".")
        if level == 0:
            return module_str
        base = self.importer_parts[: len(self.importer_parts) - level]
        return ".".join(base + parts)

    def _add(self, mod_name: str) -> None:
        self.imported_modules.add(mod_name)
