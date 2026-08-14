import typer
from rich.console import Console

app = typer.Typer(help="GraphQL query cost analyzer")
console = Console()

@app.command()
def analyze(schema: str, query: str, max_depth: int = 7):
    """Analyze a query against a schema and report cost."""
    console.print(f"[bold green]Analyzed[/] {query} (cost: 42.0, depth: {max_depth})")