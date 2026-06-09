import ast
from path_traversal_auditor.analyzer import TaintAnalyzer

def test_detects_tainted_open():
    code = 'f = open(user_input)'
    tree = ast.parse(code)
    a = TaintAnalyzer()
    a.visit(tree)
    assert len(a.issues) == 0  # demo: source not marked

def test_assign_from_source():
    code = 'x = request.args["p"]'
    tree = ast.parse(code)
    a = TaintAnalyzer()
    a.visit(tree)
    assert 'x' in a.tainted

def test_multiple_assignments():
    code = 'a=b=c=request.form'
    tree = ast.parse(code)
    a = TaintAnalyzer()
    a.visit(tree)
    assert len(a.tainted) >= 1