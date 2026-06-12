import typer
from rich.console import Console
from heap_snapshot_diff.analyzer import diff_snapshots
from heap_snapshot_diff.reporter import render_table

app = typer.Typer()
console = Console()

@app.command()
def diff(before: str, after: str, min_growth: float = 0.05):
    """Diff two heap snapshots."""
    result = diff_snapshots(before, after, min_growth)
    render_table(result, console)