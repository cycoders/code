import typer
from rich.console import Console
from .analyzer import analyze_path

app = typer.Typer()
console = Console()

@app.command()
def main(path: str, tolerance: float = 1e-9, json: bool = False):
    """Run floating point precision analysis."""
    results = analyze_path(path, tolerance)
    if json:
        console.print_json(data=results)
    else:
        for r in results:
            console.print(r)