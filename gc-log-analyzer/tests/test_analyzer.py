from gc_log_analyzer.analyzer import compute_stats
from gc_log_analyzer.parser import GCPause

def test_stats():
    pauses = [GCPause(0.1, 10.0, "young"), GCPause(0.2, 30.0, "old")]
    stats = compute_stats(pauses)
    assert stats["total_pauses"] == 2
    assert stats["max_pause_ms"] == 30.0