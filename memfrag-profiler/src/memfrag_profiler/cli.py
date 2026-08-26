import typer
from rich.console import Console
from .analyzer import analyze

app = typer.Typer()
console = Console()

@app.command()
def attach(pid: int, duration: str = "30s"):
    """Profile given pid."""
    console.print(f"Attaching to {pid}...")
    result = analyze(pid, 30)
    console.print(result)