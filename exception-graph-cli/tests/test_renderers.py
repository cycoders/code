import networkx as nx
from exception_graph_cli.renderers import to_mermaid

def test_mermaid_output():
    g = nx.DiGraph()
    g.add_edge("a.py", "b.py")
    assert "a.py --> b.py" in to_mermaid(g)