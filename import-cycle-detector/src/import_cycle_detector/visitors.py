import ast
from typing import Set


class ImportVisitor(ast.NodeVisitor):
    """
    AST visitor to extract all imported modules, resolving relative imports.
    """

    def __init__(self, current_module: str) -> None:
        self.current_module = current_module
        self.imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        level: int = node.level
        module_name: str | None = node.module

        if level == 0:
            if module_name:
                self.imported_modules.add(module_name)
        else:
            parts = self.current_module.split(".")
            if len(parts) > level:
                base_parts = parts[:-level]
                base = ".".join(base_parts)
                full_module = f"{base}.{module_name}" if module_name else base
                self.imported_modules.add(full_module)
        self.generic_visit(node)