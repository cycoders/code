import typer
from rich.console import Console
from .detector import detect_blocks

app = typer.Typer()
console = Console()

@app.command()
def main(paths: list[str] = typer.Argument(..., help="Python files or directories")):
    issues = detect_blocks(paths)
    for issue in issues:
        console.print(issue)
    raise typer.Exit(code=1 if issues else 0)