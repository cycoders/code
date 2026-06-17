import ast
from timing_side_channel_scanner.scanner import TimingVisitor

def test_no_false_positive_on_is():
    code = "if x is None: pass"
    tree = ast.parse(code)
    v = TimingVisitor()
    v.visit(tree)
    assert v.findings == []