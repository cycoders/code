import pytest
from compose_visualizer.graph import build_graph, find_cycles


def test_build_graph():
    services = {
        "a": type("Svc", (), {"depends_on": ["b", "c"]}),
        "b": type("Svc", (), {"depends_on": []}),
        "c": type("Svc", (), {"depends_on": ["b"]},
    }
    graph = build_graph(services)
    assert graph["a"] == ["b", "c"]
    assert graph["b"] == []


def test_find_cycles_no_cycle():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    cycles = find_cycles(graph)
    assert cycles == []


def test_find_cycles_with_cycle():
    graph = {"a": ["b"], "b": ["a"]}
    cycles = find_cycles(graph)
    assert len(cycles) == 1
    assert cycles[0] == ["a", "b"]