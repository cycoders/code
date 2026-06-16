import ast
import networkx as nx
from pathlib import Path

def build_call_graph(root: str) -> nx.DiGraph:
    G = nx.DiGraph()
    for pyfile in Path(root).rglob("*.py"):
        try:
            tree = ast.parse(pyfile.read_text(), filename=str(pyfile))
            module = str(pyfile.relative_to(root)).replace("/", ".")[:-3]
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    callee = node.func.id
                    G.add_edge(module, callee)
        except Exception:
            continue
    return G

def find_reachable(G: nx.DiGraph, entry: str) -> set[str]:
    if entry not in G:
        return set()
    return nx.descendants(G, entry) | {entry}