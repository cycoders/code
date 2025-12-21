import typer
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

import networkx as nx

from .graph import build_graph
from .cycles import find_cycles
from .dotgen import generate_dot


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Detect circular imports")
def detect(
    root: Path = typer.Argument(Path("."), exists=True, dir_okay=True),
    exclude: List[str] = typer.Option([], "--exclude", help="Dirs to exclude (fnmatch)"),
    min_cycle_length: int = typer.Option(2, "--min-cycle-length", min=2),
):
    typer.echo(f"Scanning [bold cyan]{root}[/bold cyan]...")

    G = build_graph(root, exclude)
    num_modules = len(G.nodes)
    num_edges = len(G.edges())

    console.print(
        f"[green]📊 {num_modules} modules, {num_edges} edges[/green]", justify="left"
    )

    cycles = [c for c in find_cycles(G) if len(c) >= min_cycle_length]

    if not cycles:
        typer.echo("[bold green]✅ No circular imports![/bold green]")
        raise typer.Exit(0)

    typer.echo(f"[bold red]🔄 {len(cycles)} cycle(s)![/bold red]")
    for idx, cycle in enumerate(cycles[:10], 1):  # Limit display
        table = Table(
            title=f"Cycle #{idx}", show_header=True, header_style="bold magenta"
        )
        table.add_column("Module", style="cyan", no_wrap=True)
        for mod in cycle:
            table.add_row(mod)
        console.print(table)

    if len(cycles) > 10:
        console.print(f"[yellow]... and {len(cycles)-10} more[/yellow]")

    raise typer.Exit(1)


@app.command(help="Export DOT graph")
def visualize(
    root: Path = typer.Argument(Path("."), exists=True),
    exclude: List[str] = typer.Option([], "--exclude"),
    output: Path = typer.Option("imports.dot", "--output", "-o", writable=True),
):
    G = build_graph(root, exclude)
    cycles = find_cycles(G)

    dot_content = generate_dot(G, cycles)
    output.write_text(dot_content, encoding="utf-8")

    console.print(
        f"[bold green]✨ Wrote [italic]{output}[/italic] ([cyan]{len(G.nodes)} nodes[/cyan])[/bold green]"
    )
    console.print("\n💡 [dim]dot -Tsvg imports.dot -o graph.svg[/dim]")
    console.print("💡 [dim]Online: [underline]edotor.net[/underline] or [underline]dreampuf.github.io/GraphvizOnline[/underline][/dim]")


if __name__ == "__main__":
    app()