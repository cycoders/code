import ast
from import_cycle_detector.visitors import ImportVisitor


class TestImportVisitor:
    def test_absolute_imports(self):
        source = """
import os
import foo.bar\nfrom sys import argv\n"""
        tree = ast.parse(source)
        visitor = ImportVisitor("pkg.mod")
        visitor.visit(tree)
        assert set(visitor.imported_modules) == {"os", "foo.bar", "sys"}

    def test_relative_imports(self):
        source = """
from .utils import foo\nfrom ..config import settings\nfrom ... import core\n"""
        tree = ast.parse(source)
        visitor = ImportVisitor("pkg.sub.mod")
        visitor.visit(tree)
        expected = {"pkg.sub.utils", "pkg.config", "pkg.core"}
        assert set(visitor.imported_modules) == expected

    def test_relative_parent(self):
        source = "from . import sibling"
        tree = ast.parse(source)
        visitor = ImportVisitor("pkg.sub.mod")
        visitor.visit(tree)
        assert "pkg.sub" in visitor.imported_modules

    def test_invalid_relative(self):
        source = "from ..... import x"  # Too high level
        tree = ast.parse(source)
        visitor = ImportVisitor("pkg.mod")
        visitor.visit(tree)
        assert visitor.imported_modules == set()