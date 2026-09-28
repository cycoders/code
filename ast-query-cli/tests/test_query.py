import ast
from pathlib import Path
from ast_query_cli.query import find_matches
from ast_query_cli.patterns import Pattern

def test_simple_match(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("x = foo.execute()\n")
    p = Pattern(ast.Call, {})
    assert len(find_matches(f, p)) == 1

def test_no_match(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("print(1)\n")
    p = Pattern(ast.Call, {"func.attr": "execute"})
    assert find_matches(f, p) == []

def test_multiline(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("def f():\n    return db.execute('SELECT 1')\n")
    p = Pattern(ast.Call, {})
    assert len(find_matches(f, p)) == 1