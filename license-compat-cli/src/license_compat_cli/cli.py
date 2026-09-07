import typer
from rich.console import Console
from .analyzer import analyze_project

app = typer.Typer(help="License compatibility checker")
console = Console()

@app.command()
def main(path: str = ".", fmt: str = "text"):
    result = analyze_project(path)
    if fmt == "json":
        console.print(result.json())
    else:
        result.render()