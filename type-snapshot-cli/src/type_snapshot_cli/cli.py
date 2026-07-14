import typer
from rich.console import Console
from .tracer import run_snapshot

app = typer.Typer(help="Capture runtime types and emit precise hints")
console = Console()

@app.command()
def snapshot(
    target: str = typer.Argument(..., help="Path to package or module"),
    out: str = typer.Option("hints.patch", "--out", help="Output patch file"),
):
    """Run tests under tracing and write minimal type hints."""
    run_snapshot(target, out)
    console.print(f"[green]Snapshot written to {out}[/green]")