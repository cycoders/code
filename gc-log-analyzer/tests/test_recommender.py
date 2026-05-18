from gc_log_analyzer.recommender import recommend
from gc_log_analyzer.parser import GCPause

def test_recommend_long_pause():
    pauses = [GCPause(1, 250.0, "old")]
    rec = recommend(pauses)
    assert "G1GC" in rec["recommendation"]