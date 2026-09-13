import libcst as cst
from async_anti_pattern_detector.engine import AntiPatternVisitor

def test_detects_blocking_sleep():
    code = "import time\nasync def f(): time.sleep(1)"
    tree = cst.parse_module(code)
    v = AntiPatternVisitor()
    tree.walk(v)
    assert len(v.findings) == 1
    assert v.findings[0].rule == "BLOCKING_CALL"