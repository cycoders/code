import typer
from rich.console import Console
from .core import compute_blast_radius

app = typer.Typer(help="Calculate blast radius of code changes")
console = Console()

@app.command()
def diff(base: str = "HEAD~1", head: str = "HEAD", format: str = "rich"):
    """Compute blast radius between two revisions."""
    result = compute_blast_radius(base, head)
    if format == "rich":
        console.print(result)
    else:
        print(result.json())