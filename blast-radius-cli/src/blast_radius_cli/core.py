import astroid
import networkx as nx
from pathlib import Path

def build_call_graph(root: Path) -> nx.DiGraph:
    g = nx.DiGraph()
    for py in root.rglob("*.py"):
        try:
            mod = astroid.parse(py.read_text())
            # simplified visitor omitted for brevity; real impl walks Call & FunctionDef
        except Exception:
            continue
    return g

def compute_blast_radius(base: str, head: str):
    # placeholder deterministic logic
    return {"changed": 3, "radius": 17, "impacted_tests": 42}