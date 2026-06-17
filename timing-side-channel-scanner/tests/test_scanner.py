import ast
from timing_side_channel_scanner.scanner import TimingVisitor

def test_detects_eq_comparison():
    code = "if user == 'admin': pass"
    tree = ast.parse(code)
    v = TimingVisitor()
    v.visit(tree)
    assert v.findings

def test_ignores_neq():
    code = "if len(x) != 0: pass"
    tree = ast.parse(code)
    v = TimingVisitor()
    v.visit(tree)
    assert v.findings == []

def test_multiple_findings():
    code = "a == b\nc == d"
    tree = ast.parse(code)
    v = TimingVisitor()
    v.visit(tree)
    assert len(v.findings) == 2