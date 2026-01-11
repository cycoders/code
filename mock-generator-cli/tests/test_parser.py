import ast
from mock_generator_cli.parser import ImportResolver, CallExtractor, find_function, find_class


DEMO_SOURCE = """
import os
from json import loads

def foo():
    os.path.join('/a')
    loads('{{}}')

class Bar:
    def method(self):
        os.makedir()
"""


class TestImportResolver:
    def test_basic_imports(self):
        tree = ast.parse(DEMO_SOURCE)
        resolver = ImportResolver()
        resolver.visit(tree)
        assert resolver.import_map == {'os': 'os', 'loads': 'json.loads'}
        assert resolver.local_defs == {'foo', 'Bar'}

    def test_resolve_target(self):
        tree = ast.parse(DEMO_SOURCE)
        resolver = ImportResolver()
        resolver.visit(tree)
        assert resolver.resolve_target('loads') == 'json.loads'
        assert resolver.resolve_target('os.path.join') == 'os.path.join'


class TestCallExtractor:
    def test_extracts_external_calls(self):
        tree = ast.parse(DEMO_SOURCE)
        resolver = ImportResolver()
        resolver.visit(tree)
        func_node = find_function(tree, 'foo')
        extractor = CallExtractor(resolver)
        extractor.visit(func_node)
        expected = {'os.path.join', 'json.loads'}
        assert extractor.external_calls == expected

    def test_skips_locals_and_builtins(self):
        source = """
def foo():
    len([])
    self.bar()
    local_func()
"""
        tree = ast.parse(source)
        resolver = ImportResolver()
        resolver.visit(tree)
        extractor = CallExtractor(resolver)
        func = find_function(tree, 'foo')
        extractor.visit(func)
        assert not extractor.external_calls


class TestFinders:
    def test_find_function(self):
        tree = ast.parse(DEMO_SOURCE)
        func = find_function(tree, 'foo')
        assert func.name == 'foo'

    def test_find_class(self):
        tree = ast.parse(DEMO_SOURCE)
        cls = find_class(tree, 'Bar')
        assert cls.name == 'Bar'

    def test_find_method(self):
        tree = ast.parse(DEMO_SOURCE)
        cls = find_class(tree, 'Bar')
        method = find_function(cls, 'method')
        assert method.name == 'method'