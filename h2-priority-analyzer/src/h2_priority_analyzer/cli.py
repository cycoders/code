import typer
from pathlib import Path
from rich import print as rprint
from rich.traceback import install

install(show_locals=True)

from .parser import parse_netlog
from .graph import PriorityGraph
from .visualizer import render_tree, render_waterfall, render_suggestions, render_chains


app = typer.Typer(no_args_is_help=True)


@app.command()
def analyze(
    netlog_path: Path = typer.Argument(..., help="Chrome netlog JSONL"),
    tree: bool = typer.Option(True, "--tree/--no-tree"),
    waterfall: bool = typer.Option(True, "--waterfall/--no-waterfall"),
    suggestions: bool = typer.Option(True, "--suggestions/--no-suggestions"),
    min_duration: float = typer.Option(0, "--min-duration"),
    output: Optional[Path] = typer.Option(None, "--output", help="SVG/PNG/JSON"),
):
    """Analyze HTTP/2 priorities from netlog."""

    if not netlog_path.exists():
        raise typer.BadParameter(f"File not found: {netlog_path}")

    rprint(f"🔍 Analyzing [bold]{netlog_path}[/bold] ({netlog_path.stat().st_size / 1024:.0f}KB)")

    streams = parse_netlog(netlog_path)
    streams = [s for s in streams if (s.duration or 0) >= min_duration]

    if not streams:
        rprint("❌ No qualifying streams found.")
        raise typer.Exit(1)

    rprint(f"📊 Found {len(streams)} streams, avg {sum(s.duration or 0 for s in streams)/len(streams):.0f}ms")

    graph = PriorityGraph(streams)

    if tree:
        render_tree(streams, graph)

    chains = graph.find_longest_chains()
    render_chains(chains)

    if waterfall:
        render_waterfall(streams, graph, output)

    if suggestions:
        render_suggestions(graph)


if __name__ == "__main__":
    app()