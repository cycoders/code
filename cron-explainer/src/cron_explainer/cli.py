import typer
from rich.console import Console
from rich.table import Table
from cron_explainer.parser import explain, next_runs

app = typer.Typer(help="Explain cron expressions and predict future runs")
console = Console()

@app.command()
def main(expression: str, timezone: str = "UTC", count: int = 5):
    """Explain a cron expression and show upcoming execution times."""
    try:
        desc = explain(expression)
        runs = next_runs(expression, timezone, count)
        console.print(f"[bold]Description:[/bold] {desc}")
        table = Table(title="Upcoming runs")
        table.add_column("Time")
        for r in runs:
            table.add_row(r.isoformat())
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")