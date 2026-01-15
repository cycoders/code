import sys
import typer
import logging
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .analyzer import build_call_graph
from .viz import render_graph, format_mermaid

app = typer.Typer(add_completion=False)
console = Console()
logging.basicConfig(level=logging.WARNING)

@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Python file or directory"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file (png/svg/dot/mmd)"),
    exclude: List[str] = typer.Option([], "--exclude/"),
    stats: bool = typer.Option(True, "--stats/--no-stats"),
):
    """Build and visualize Python function call graph."""
    graph = build_call_graph(path, exclude)

    if stats:
        edges = sum(len(callees) for callees in graph.values())
        nodes = len(graph)
        avg_degree = edges / nodes if nodes else 0
        table = Table(title="Call Graph Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_row("Functions", str(nodes))
        table.add_row("Call edges", str(edges))
        table.add_row("Avg out-degree", f"{avg_degree:.2f}")
        console.print(table)

    mermaid_md = format_mermaid(graph)
    console.print(Panel(mermaid_md, title="[Mermaid Preview] Paste to mermaid.live", expand=False))

    if output:
        try:
            render_graph(graph, output)
            console.print(f"[green]Saved:[/green] {output}")
        except Exception as e:
            typer.echo(f"[red]Viz error:[/red] {e}. Install graphviz?", err=True)

if __name__ == "__main__":
    app()