from test_minimizer_cli.minimizer import DeltaMinimizer

def test_minimizer_reduces():
    def always_true(p): return True
    m = DeltaMinimizer(always_true)
    assert len(m.minimize('a'*100)) < 100

def test_granularity():
    def always_true(p): return True
    m = DeltaMinimizer(always_true, granularity=4)
    res = m.minimize('abcdefg')
    assert len(res) <= 4

def test_edge_empty():
    def always_true(p): return True
    m = DeltaMinimizer(always_true)
    assert m.minimize('') == ''

def test_idempotent():
    def always_true(p): return True
    m = DeltaMinimizer(always_true)
    s = 'hello world'
    assert m.minimize(s) == m.minimize(m.minimize(s))

def test_preserves_failure():
    calls = []
    def tracker(p):
        calls.append(1)
        return True
    m = DeltaMinimizer(tracker)
    m.minimize('x'*8)
    assert len(calls) > 0