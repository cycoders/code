import networkx as nx
from blast_radius_cli.graph import transitive_closure

def test_transitive_closure():
    g = nx.DiGraph()
    g.add_edges_from([("a", "b"), ("b", "c")])
    assert transitive_closure(g, {"a"}) == {"a", "b", "c"}

def test_depth_limit():
    g = nx.DiGraph()
    g.add_edges_from([("a", "b"), ("b", "c"), ("c", "d")])
    assert len(transitive_closure(g, {"a"}, max_depth=1)) == 2