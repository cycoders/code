import pytest
import networkx as nx
from env_dependency_analyzer.analyzer import analyze_graph, generate_dot


def test_analyze_graph():
    G = nx.DiGraph([("A", "B"), ("B", "A")])  # cycle
    defined = {"A", "B"}
    stats = analyze_graph(G, defined)
    assert len(stats["cycles"]) == 1
    assert stats["external"] == set()

    G2 = nx.DiGraph([("C", "EXT")])
    defined2 = {"C"}
    stats2 = analyze_graph(G2, defined2)
    assert "EXT" in stats2["external"]
    assert not stats2["cycles"]


def test_generate_dot():
    G = nx.DiGraph([("DB_URL", "DB_HOST")])
    defined = {"DB_URL", "DB_HOST"}
    dot = generate_dot(G, defined)
    assert "digraph" in dot
    assert "DB_URL" in dot
    assert "lightgreen" in dot
