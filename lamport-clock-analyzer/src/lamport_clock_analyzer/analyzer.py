import networkx as nx
from .models import Event, Graph

def build_graph(events: list[Event]) -> Graph:
    g = nx.DiGraph()
    last = {}
    for e in sorted(events, key=lambda x: x.ts):
        g.add_node(f"{e.pid}:{e.ts}")
        if e.pid in last:
            g.add_edge(last[e.pid], f"{e.pid}:{e.ts}")
        last[e.pid] = f"{e.pid}:{e.ts}"
    return Graph(nodes=set(g.nodes), edges=list(g.edges))