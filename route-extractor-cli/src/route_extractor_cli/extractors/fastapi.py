import ast
from typing import Set, List

from ..models import Route
from ..utils import parse_path_params
from .base import BaseExtractor


class FastAPIExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.app_vars: Set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "fastapi":
            for alias in node.names:
                if alias.name in ("FastAPI", "APIRouter"):
                    self.app_vars.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                value = node.value
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                    if value.func.id == "FastAPI" or value.func.id == "APIRouter":
                        self.app_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in ("get", "post", "put", "delete", "patch", "options", "head")
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.app_vars
            and node.args
        ):
            path_arg = node.args[0]
            path = getattr(path_arg, "s", "") if isinstance(path_arg, ast.Str) else getattr(path_arg, "value", "") if isinstance(path_arg, ast.Constant) else ""
            handler = "unknown"
            if len(node.args) > 1 and isinstance(node.args[1], ast.Name):
                handler = node.args[1].id
            method = node.func.attr.upper()
            params = parse_path_params(path)
            self.add_route([method], path, f"{node.func.value.id}.{handler}", params)
        self.generic_visit(node)
