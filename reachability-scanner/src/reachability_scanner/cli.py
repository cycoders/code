import typer
from rich.console import Console
from reachability_scanner.graph import build_call_graph, find_reachable
from reachability_scanner.vuln import load_vulns, filter_reachable

app = typer.Typer(help="Reachability scanner for Python")
console = Console()

@app.command()
def scan(path: str, entry: str = "app:main", vuln_db: str = "vulns.json"):
    """Scan project for reachable vulnerabilities."""
    console.print(f"[bold]Building call graph for[/] {path}")
    graph = build_call_graph(path)
    reachable = find_reachable(graph, entry)
    vulns = load_vulns(vuln_db)
    hits = filter_reachable(reachable, vulns)
    console.print(f"[green]Found {len(hits)} reachable vulnerabilities[/]")
    for h in hits:
        console.print(f"  - {h}")