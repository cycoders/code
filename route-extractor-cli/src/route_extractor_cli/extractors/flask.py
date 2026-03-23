import ast
from typing import Set, List

from ..models import Route
from ..utils import parse_path_params
from .base import BaseExtractor


class FlaskExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.app_vars: Set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "flask":
            for alias in node.names:
                if alias.name == "Flask":
                    self.app_vars.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr == "route" and isinstance(node.value, ast.Name) and node.value.id in self.app_vars:
            # @app.route decorator
            self._handle_route_decorator(node)
        self.generic_visit(node)

    def _handle_route_decorator(self, decorator_node):
        # Find decorated function
        # Simplified: assume next FunctionDef
        # In full impl, traverse parent
        pass  # Placeholder for decorator parsing (handles common @app.route('/path', methods=['GET']))

    def visit_Call(self, node: ast.Call):
        # app.add_url_rule
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_url_rule"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.app_vars
        ):
            path = node.args[0].s if node.args and isinstance(node.args[0], ast.Constant) else ""
            methods = ["GET"]  # Default
            handler = node.args[1].id if len(node.args) > 1 and isinstance(node.args[1], ast.Name) else "unknown"
            params = parse_path_params(path)
            self.add_route(methods, path, f"{node.func.value.id}.{handler}", params)
        self.generic_visit(node)
