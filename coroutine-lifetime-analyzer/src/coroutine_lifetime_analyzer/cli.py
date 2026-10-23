import typer
from rich.console import Console
from .analyzer import analyze_path

app = typer.Typer(help="Detect leaked coroutines and task lifetime issues")
console = Console()

@app.command()
def main(path: str, trace: bool = False, duration: float = 0.0):
    """Analyze asyncio code for coroutine leaks."""
    results = analyze_path(path, enable_trace=trace, duration=duration)
    for r in results:
        console.print(r)