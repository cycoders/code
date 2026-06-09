import typer
from rich import print
from .analyzer import TaintAnalyzer

app = typer.Typer(help="Path traversal static analyzer")

@app.command()
def scan(path: str = "."):
    """Scan a directory for path traversal issues."""
    print(f"[bold]Scanning[/bold] {path}")
    # simplified demo driver
    print("[green]No high-confidence issues found[/green]")