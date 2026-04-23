from h2_priority_analyzer.models import Stream, PriorityInfo
from h2_priority_analyzer.graph import PriorityGraph


def test_build_graph():
    streams = [
        Stream(id=1, priority=PriorityInfo(dependency=0)),
        Stream(id=2, priority=PriorityInfo(dependency=1)),
    ]
    graph = PriorityGraph(streams)
    assert 2 in graph.adj[1]


def test_levels():
    streams = [
        Stream(id=1, priority=PriorityInfo(dependency=0)),
        Stream(id=2, priority=PriorityInfo(dependency=1)),
        Stream(id=3, priority=PriorityInfo(dependency=2)),
    ]
    graph = PriorityGraph(streams)
    levels = graph.compute_levels()
    assert levels[1] == 0
    assert levels[3] == 2


def test_chains():
    streams = [
        Stream(id=1, duration=50, priority=PriorityInfo(dependency=0)),
        Stream(id=2, duration=100, priority=PriorityInfo(dependency=1)),
    ]
    graph = PriorityGraph(streams)
    chains = graph.find_longest_chains()
    assert len(chains) == 1
    assert chains[0].total_block_ms == 150
