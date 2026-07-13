import typer
from rich.console import Console
from .analyzer import analyze_path

app = typer.Typer()
console = Console()

@app.command()
def main(path: str, format: str = "text", threshold: str = "medium"):
    """Analyze path for priority inversion risks."""
    results = analyze_path(path, threshold)
    if format == "json":
        console.print_json(data=results)
    else:
        for r in results:
            console.print(r)