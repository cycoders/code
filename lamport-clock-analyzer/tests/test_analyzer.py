from lamport_clock_analyzer.models import Event
from lamport_clock_analyzer.analyzer import build_graph

def test_build_graph():
    events = [Event(1,"a",{}), Event(2,"a",{})]
    g = build_graph(events)
    assert len(g.nodes) == 2