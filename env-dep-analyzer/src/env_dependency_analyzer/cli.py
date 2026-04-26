import sys
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .parser import scan_directory
from .analyzer import analyze_graph, generate_dot

app = typer.Typer()
console = Console()

@app.command()
def scan(path: Path = "."):
    """Scan directory for .env and docker-compose files, print stats."""
    defined, edges, files = scan_directory(path)
    import networkx as nx
    G = nx.DiGraph(edges)
    stats = analyze_graph(G, defined)

    table = Table(title="Env Dep Analyzer Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("Files scanned", str(len(files)))
    table.add_row("Defined vars", str(len(defined)))
    table.add_row("Edges", str(len(edges)))
    table.add_row("External vars", str(len(stats["external"])))
    table.add_row("Cycles", "Yes" if stats["cycles"] else "No")
    console.print(table)

    if stats["cycles"]:
        console.print("[red]Cycles:[/red]")
        for cycle in stats["cycles"][0:5]:
            console.print(f"  {' -> '.join(cycle)} → (cycle)")
    else:
        console.print("[green]No cycles ✓[/green]")

    if stats["external"]:
        console.print("[yellow]External vars:[/yellow]")
        for v in sorted(stats["external"]):
            console.print(f"  {v}")

@app.command()
def viz(path: Path = ".", output: Path = None):
    """Generate Graphviz DOT file."""
    defined, edges, _ = scan_directory(path)
    import networkx as nx
    G = nx.DiGraph(edges)
    dot = generate_dot(G, defined)
    if output:
        output.write_text(dot)
        console.print(f"[green]DOT saved: {output}[/green]")
    else:
        print(dot)

@app.command()
def check(path: Path = ".", fail_on_cycle: bool = True):
    """Check for cycles (exit 1 if found)."""
    defined, edges, _ = scan_directory(path)
    import networkx as nx
    G = nx.DiGraph(edges)
    cycles = list(nx.simple_cycles(G)) if G.number_of_nodes() > 0 else []
    if fail_on_cycle and cycles:
        console.print("[red]Cycles detected![/red]")
        for cycle in cycles[:3]:
            console.print(f"  {' -> '.join(cycle)}")
        raise typer.Exit(code=1)
    console.print("[green]No issues ✓[/green]")

def main():
    app(prog_name="env-dep-analyzer")

if __name__ == "__main__":
    main()
