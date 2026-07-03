import ast
from exception_graph_cli.analyzer import extract_exceptions

def test_extract_simple_raise():
    tree = ast.parse("raise ValueError('x')")
    assert extract_exceptions(tree) == {"ValueError"}

def test_ignore_bare_raise():
    tree = ast.parse("try: pass\nexcept: raise")
    assert extract_exceptions(tree) == set()