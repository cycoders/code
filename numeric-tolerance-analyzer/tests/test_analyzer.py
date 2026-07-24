import libcst as cst
from numeric_tolerance_analyzer.analyzer import ToleranceAnalyzer

def test_detects_compare():
    code = "assert a == b"
    tree = cst.parse_module(code)
    visitor = ToleranceAnalyzer()
    tree.visit(visitor)
    assert len(visitor.results) == 1