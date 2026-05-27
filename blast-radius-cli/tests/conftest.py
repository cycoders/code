import pytest

@pytest.fixture
def sample_graph():
    import networkx as nx
    g = nx.DiGraph()
    g.add_edges_from([("mod.a", "mod.b"), ("mod.b", "mod.c")])
    return g