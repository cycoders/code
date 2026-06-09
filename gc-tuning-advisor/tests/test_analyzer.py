from gc_tuning_advisor.analyzer import analyze
from gc_tuning_advisor.models import GCEvent

def test_analyze_p95():
    ev = [GCEvent(0, 100, 0, 2.5, 0), GCEvent(0, 90, 0, 3.1, 0)]
    res = analyze(ev)
    assert 'p95' in res[0]