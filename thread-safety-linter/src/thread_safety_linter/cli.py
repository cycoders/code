import typer
from rich.console import Console
from .analyzer import analyze_path

app = typer.Typer(help="Thread safety static analyzer")
console = Console()

@app.command()
def main(path: str = ".", fail_on: str = "medium"):
    issues = analyze_path(path)
    for issue in issues:
        console.print(issue)
    if issues:
        raise typer.Exit(code=1)
