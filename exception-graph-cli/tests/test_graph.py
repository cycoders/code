from pathlib import Path
from exception_graph_cli.graph import build_graph

def test_empty_graph():
    g = build_graph([])
    assert g.number_of_nodes() == 0