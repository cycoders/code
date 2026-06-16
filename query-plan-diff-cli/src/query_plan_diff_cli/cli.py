import typer
from rich.console import Console
from query_plan_diff_cli.diff import diff_plans

app = typer.Typer(help="Structural PostgreSQL EXPLAIN diff tool")
console = Console()

@app.command()
def diff(base: str, head: str, query_file: str = None):
    """Compare two plans and report differences."""
    result = diff_plans(base, head, query_file)
    console.print(result)