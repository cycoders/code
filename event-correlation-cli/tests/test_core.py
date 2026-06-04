from event_correlation_cli.core import correlate

def test_basic_correlation():
    events = [
        {"ts": "2025-01-01T00:00:00Z", "trace_id": "abc", "msg": "start"},
        {"ts": "2025-01-01T00:00:02Z", "trace_id": "abc", "msg": "end"},
    ]
    chains = correlate(events, ["trace_id"], "5s")
    assert len(chains) == 1
    assert chains[0]["score"] == 2

def test_window_excludes():
    events = [
        {"ts": "2025-01-01T00:00:00Z", "trace_id": "abc"},
        {"ts": "2025-01-01T00:00:10Z", "trace_id": "abc"},
    ]
    chains = correlate(events, ["trace_id"], "3s")
    assert len(chains) == 0