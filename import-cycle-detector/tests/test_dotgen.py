import networkx as nx
from import_cycle_detector.dotgen import generate_dot


def test_generate_dot():
    G = nx.DiGraph()
    G.add_edges_from([("a", "b"), ("b", "a"), ("c", "d")])
    cycles = [["a", "b"]]
    dot = generate_dot(G, cycles)
    assert "digraph" in dot
    assert '"a" -> "b" [color="red"' in dot
    assert '"c" -> "d" [color="black"' in dot
    assert '"a" [fillcolor="yellow"' in dot


def test_no_cycles():
    G = nx.DiGraph([("a", "b")])
    dot = generate_dot(G, [])
    assert '"a" [fillcolor="lightblue"' in dot