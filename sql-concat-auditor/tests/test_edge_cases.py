import ast
from sql_concat_auditor.scanner import SQLConcatVisitor

def test_multiline_concat():
    code = 'q = "SELECT * " + "FROM users " + "WHERE id=" + x\ncursor.execute(q)'
    tree = ast.parse(code)
    v = SQLConcatVisitor()
    v.visit(tree)
    assert len(v.findings) == 1