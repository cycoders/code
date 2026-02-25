import networkx as nx
from typing import Any

import rich.console
import rich.table
from rich.panel import Panel


def render_mermaid(G: nx.DiGraph) -> str:
    """Generate Mermaid flowchart TD code."""
    safe_id = lambda n: str(n).replace(" ", "_").replace("-", "_").replace(".", "_")

    lines = ["flowchart TD"]

    # Nodes
    for node, data in G.nodes(data=True):
        node_id = safe_id(node)
        node_type = data.get("type", "host")
        shape = {
            "host_pattern": "[]",
            "hostname": "(())",
            "proxyjump": "{{{{}}}"",
            "proxycommand": ">{{}}</>"
        }.get(node_type, "[]")
        lines.append(f"    {node_id}{shape}")

    # Edges
    for u, v, data in G.edges(data=True):
        label = data.get("relation", "links").replace("_", " ").title()
        lines.append(f"    {safe_id(u)} -->|{label}| {safe_id(v)}")

    return "\n".join(lines) + "\n"


def render_stats_table(G: nx.DiGraph, console: rich.console.Console) -> None:
    """Rich table with graph stats."""
    has_cycle = bool(next(nx.find_cycle(G, orientation="original"), None))

    table = rich.table.Table(title="[bold cyan]SSH Graph Stats[/bold cyan]")
    table.add_column("Metric", style="magenta")
    table.add_column("Value", style="green")

    table.add_row("Nodes", str(len(G.nodes)))
    table.add_row("Edges", str(len(G.edges)))
    table.add_row("Is DAG", "[green]Yes[/]" if nx.is_directed_acyclic_graph(G) else "[red]No[/]")
    table.add_row("Cycles", "[red]Yes[/]" if has_cycle else "[green]No[/]")
    table.add_row("Density", f"{nx.density(G):.2%}")

    console.print(table)

    # Top hubs
    degrees = dict(G.out_degree())
    top_hubs = sorted(degrees, key=degrees.get, reverse=True)[:5]
    console.print("\n[bold]Top Proxy Hubs:[/] " + ", ".join(top_hubs))