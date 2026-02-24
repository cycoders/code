import typer
from pathlib import Path
import rich.traceback

rich.traceback.install(show_locals=True)

from rich.console import Console

from . import __version__
from .parser import parse_file
from .stats import print_trace_stats, print_bottlenecks
from .visualizer import generate_waterfall_html


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command(help="Analyze trace file(s) with stats and optional viz")
def analyze(
    paths: list[Path] = typer.Argument(..., help="JSON trace file(s) or dir"),
    output: Optional[Path] = typer.Option(
        None, "--output/-o", help="Output dir for HTML waterfalls"
    ),
    top_n: int = typer.Option(10, "--top-n", min=1, max=50, help="Top bottlenecks"),
):
    """Main analysis: stats + bottlenecks + optional waterfalls."""

    all_trees = {}
    for path in paths:
        if path.is_dir():
            json_files = list(path.glob("**/*.json"))
            if not json_files:
                console.print(f"[yellow]No .json in {path}[/]")
                continue
            for jf in json_files:
                trees = parse_file(jf, console)
                all_trees.update(trees)
        else:
            trees = parse_file(path, console)
            all_trees.update(trees)

    for trace_id, roots in all_trees.items():
        console.rule(f"Trace {trace_id[:16]}...", style="bold cyan")
        print_trace_stats(roots, f"Stats: {trace_id[:16]}...")
        print_bottlenecks(roots, top_n)

        if output:
            generate_waterfall_html(roots, output, trace_id, console)


@app.command(help="Print version")
def version():
    console.print(f"trace-analyzer-cli v{__version__}")


if __name__ == "__main__":
    app()
