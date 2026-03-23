import ast
from typing import List

from ..models import Route
from ..utils import parse_path_params
from .base import BaseExtractor


class DjangoExtractor(BaseExtractor):
    def visit_Assign(self, node: ast.Assign):
        # urlpatterns = [...]
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "urlpatterns":
                if isinstance(node.value, ast.List):
                    self._extract_from_urlpatterns(node.value)
        self.generic_visit(node)

    def _extract_from_urlpatterns(self, url_list: ast.List):
        for elt in url_list.elts:
            if isinstance(elt, ast.Call):
                self._handle_path_call(elt)
        
    def _handle_path_call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in ("path", "re_path"):
            path_arg = node.args[0] if node.args else None
            path = path_arg.s if path_arg and isinstance(path_arg, ast.Constant) else ""
            handler = "unknown"
            for kw in node.keywords:
                if kw.arg == "name":
                    handler = kw.value.s if isinstance(kw.value, ast.Constant) else kw.value.id
                    break
            method = "GET,HEAD,POST"  # path defaults
            params = parse_path_params(path)
            self.add_route(method.split(','), path, f"urls.{handler}", params)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "django.urls":
            pass  # Track
        self.generic_visit(node)
