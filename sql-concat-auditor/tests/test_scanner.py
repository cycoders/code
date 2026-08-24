import ast
from sql_concat_auditor.scanner import SQLConcatVisitor

def test_detects_plus_concat():
    code = 'cursor.execute("SELECT * FROM t WHERE id=" + user_id)'
    tree = ast.parse(code)
    v = SQLConcatVisitor()
    v.visit(tree)
    assert len(v.findings) == 1

def test_ignores_parameterized():
    code = 'cursor.execute("SELECT * FROM t WHERE id=%s", (user_id,))'
    tree = ast.parse(code)
    v = SQLConcatVisitor()
    v.visit(tree)
    assert len(v.findings) == 0

def test_detects_fstring():
    code = 'cursor.execute(f"SELECT * FROM t WHERE id={user_id}")'
    tree = ast.parse(code)
    v = SQLConcatVisitor()
    v.visit(tree)
    assert len(v.findings) == 1