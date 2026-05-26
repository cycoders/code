import ast
from async_block_detector.detector import BlockingVisitor

def test_detects_sleep():
    code = "async def f(): time.sleep(1)"
    tree = ast.parse(code)
    v = BlockingVisitor()
    v.visit(tree)
    assert len(v.issues) == 1

def test_ignores_sync():
    code = "def f(): time.sleep(1)"
    tree = ast.parse(code)
    v = BlockingVisitor()
    v.visit(tree)
    assert len(v.issues) == 0

def test_detects_requests():
    code = "async def f(): requests.get('x')"
    tree = ast.parse(code)
    v = BlockingVisitor()
    v.visit(tree)
    assert len(v.issues) == 1