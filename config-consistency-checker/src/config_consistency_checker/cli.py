import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def check(files: list[str], policy: str = None):
    console.print("[green]Running consistency check...[/]")