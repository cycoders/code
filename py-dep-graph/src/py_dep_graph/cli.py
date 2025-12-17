import sys
import typer
from pathlib import Path
from typing import Optional

from rich.console import Console

from .builder import build_graph
from .graph import DepGraph
from .visualizer import print_tree, to_dot


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Display dependency graph")
def graph(
    root: Path = typer.Argument(Path("."), help="Project root directory"),
    fmt: str = typer.Option("tree", "--format/-f", help="Output: tree or dot"),
    output: Optional[Path] = typer.Option(None, "--output/-o", help="DOT output file"),
):
    graph_obj = build_graph(root)
    if fmt == "tree":
        print_tree(graph_obj, console)
    elif fmt == "dot":
        if output:
            output.write_text("", encoding="utf-8")
            with output.open("w") as f:
                to_dot(graph_obj, f)
            console.print(f"[green]✓ DOT exported to {output}")
        else:
            to_dot(graph_obj, sys.stdout)
    else:
        raise typer.BadParameter(f"Invalid format: {fmt}. Use 'tree' or 'dot'.")


@app.command(help="Detect circular dependencies")
def cycles(root: Path = typer.Argument(Path("."))):
    graph_obj = build_graph(root)
    cycles_list = graph_obj.cycles()
    if not cycles_list:
        console.print("[bold green]✓ No cycles detected![/]")
        raise typer.Exit(0)
    console.print(f"[bold red]Found {len(cycles_list)} cycle(s):[/]")
    for i, cycle in enumerate(cycles_list, 1):
        cycle_str = " -> ".join(cycle) + " -> " + cycle[0]
        console.print(f"  {i}. [red]{cycle_str}[/]"))


@app.command(help="Show dependency metrics")
def metrics(root: Path = typer.Argument(Path("."))):
    graph_obj = build_graph(root)
    cycles_n = len(graph_obj.cycles())
    avg_degree = graph_obj.num_edges / graph_obj.num_nodes if graph_obj.num_nodes else 0
    max_degree = max((len(graph_obj.adj.get(n, set())) for n in graph_obj.nodes), default=0)

    table = typer.rich.table.Table(title="Dependency Metrics", box=typer.rich.table.ROUNDROBIN)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Nodes", str(graph_obj.num_nodes))
    table.add_row("Edges", str(graph_obj.num_edges))
    table.add_row("Avg out-degree", f"{avg_degree:.2f}")
    table.add_row("Max out-degree", str(max_degree))
    table.add_row("Cycles", str(cycles_n))
    console.print(table)


def main() -> None:
    """CLI entrypoint."""
    if __name__ == "__main__":
        app(prog_name="py-dep-graph")


if __name__ == "__main__":
    main()
