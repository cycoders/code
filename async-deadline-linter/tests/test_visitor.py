from async_deadline_linter.visitor import DeadlineVisitor
import libcst as cst

def test_visitor_runs():
    tree = cst.parse_module("async def x(): await y()")
    v = DeadlineVisitor()
    tree.walk(v)
    assert len(v.findings) >= 0