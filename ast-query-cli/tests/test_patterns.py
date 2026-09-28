import ast
from ast_query_cli.patterns import Pattern

def test_attr_match():
    p = Pattern(ast.Attribute, {"attr": "execute"})
    node = ast.parse("x.execute").body[0].value
    assert p.matches(node)

def test_type_mismatch():
    p = Pattern(ast.Call, {})
    node = ast.parse("x = 1").body[0].value
    assert not p.matches(node)