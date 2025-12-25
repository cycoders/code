import ast
from pathlib import Path
from typing import List

from .models import ClassInfo, Method


class ASTClassVisitor(ast.NodeVisitor):
    """AST visitor to extract classes, methods, and attributes."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.classes: List[ClassInfo] = []
        self.current_class: ClassInfo | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Extract bases (simple names only for v1)
        bases = [
            base.id
            for base in node.bases
            if isinstance(base, ast.Name)
        ]
        self.current_class = ClassInfo(
            name=node.name,
            module=self.module_name,
            bases=bases,
        )
        self.classes.append(self.current_class)
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.current_class is not None:
            decorators = [dec.id for dec in node.decorator_list if isinstance(dec, ast.Name)]
            is_static = "staticmethod" in decorators
            is_classmethod = "classmethod" in decorators
            self.current_class.methods.append(
                Method(
                    name=node.name,
                    is_static=is_static,
                    is_classmethod=is_classmethod,
                )
            )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if (
            self.current_class is not None
            and isinstance(node.target, ast.Name)
            and not node.target.id.startswith("_")
        ):
            self.current_class.attributes.append(node.target.id)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if (
            self.current_class is not None
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and not node.targets[0].id.startswith("_")
        ):
            self.current_class.attributes.append(node.targets[0].id)
        self.generic_visit(node)
