import ast
from typing import List

from ..models import Route


class BaseExtractor(ast.NodeVisitor):
    routes: List[Route] = []

    def add_route(self, methods: List[str], path: str, handler: str, parameters: List[dict] = None):
        params = [Parameter(**p) for p in (parameters or [])]
        self.routes.append(Route(methods=methods, path=path, handler=handler, parameters=params))
