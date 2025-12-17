import ast
from py_dep_graph.finder import ImportFinder


class TestImportFinder:
    def test_absolute_import(self):
        code = "import foo.bar.baz"
        tree = ast.parse(code)
        finder = ImportFinder("pkg.mod")
        finder.visit(tree)
        assert "foo.bar.baz" in finder.imported_modules

    def test_import_from_absolute(self):
        code = "from foo.bar import baz"
        tree = ast.parse(code)
        finder = ImportFinder("a.b.c")
        finder.visit(tree)
        assert "foo.bar" in finder.imported_modules

    def test_relative_sibling(self):
        code = "from .utils import helper"
        tree = ast.parse(code)
        finder = ImportFinder("main.mod")
        finder.visit(tree)
        assert "main.utils" in finder.imported_modules

    def test_parent_relative(self):
        code = "from ..utils import helper"
        tree = ast.parse(code)
        finder = ImportFinder("pkg.sub.mod")
        finder.visit(tree)
        assert "pkg.utils" in finder.imported_modules

    def test_deep_relative(self):
        code = "from ...core import api"
        tree = ast.parse(code)
        finder = ImportFinder("a.b.c.d")
        finder.visit(tree)
        assert "core" in finder.imported_modules
