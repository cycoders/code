import libcst as cst
from import_optimizer.analyzer import LoadedNamesVisitor, get_provided_names


class TestGetProvidedNames:
    def test_import(self):
        node = cst.parse_module("import os").body[0]
        assert get_provided_names(node) == {"os"}

    def test_import_alias(self):
        node = cst.parse_module("import os as operating_sys").body[0]
        assert get_provided_names(node) == {"operating_sys"}

    def test_from_import(self):
        node = cst.parse_module("from os import path").body[0]
        assert get_provided_names(node) == {"path"}

    def test_star(self):
        node = cst.parse_module("from os import *").body[0]
        assert get_provided_names(node) == {"__all__star__"}


class TestLoadedNamesVisitor:
    def test_loads(self, parse_module):
        module = parse_module("import os\nprint(os.path)")
        visitor = LoadedNamesVisitor()
        visitor.visit(module)
        assert "os" in visitor.loaded
        assert "path" in visitor.loaded
        assert "print" in visitor.loaded

    def test_no_store(self, parse_module):
        module = parse_module("x = 1")
        visitor = LoadedNamesVisitor()
        visitor.visit(module)
        assert "x" not in visitor.loaded  # store only