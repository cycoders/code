from orm_nplus1_detector.core import Finding

def test_finding_creation():
    f = Finding('app.py', 42, 15, 'Use selectinload')
    assert f.line == 42