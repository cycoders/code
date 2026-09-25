import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def scan(path: str, update: bool = False):
    console.print(f"Scanning {path}...")