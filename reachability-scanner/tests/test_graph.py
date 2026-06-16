import ast
import networkx as nx
from reachability_scanner.graph import build_call_graph, find_reachable

def test_simple_call_graph(tmp_path):
    (tmp_path / "a.py").write_text("def main(): foo()\ndef foo(): pass")
    g = build_call_graph(str(tmp_path))
    assert "foo" in find_reachable(g, "a.main")