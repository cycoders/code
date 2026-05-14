import typer
from rich.console import Console
from rich.traceback import install
import rich_click as click

from .parser import parse_metrics
from .calculator import compute_burn_rates
from .viz import render_results

install(show_locals=False)

app = typer.Typer(help="SLO Burn Rate Calculator", pretty_exceptions_enable=False)
console = Console()

@app.command()
def main(
    input_path: str = typer.Argument(..., help="Path to JSONL or CSV file with metrics"),
    ts_col: str = typer.Option("timestamp", "--ts-col", help="Timestamp column"),
    latency_col: str | None = typer.Option(None, "--latency-col", help="Latency column (ms)"),
    status_col: str | None = typer.Option(None, "--status-col", help="Status code column"),
    error_above: int = typer.Option(400, "--error-above", help="Error if status >= this"),
    metric: str = typer.Option("error_rate", "--metric", choices=["error_rate", "latency_p99"]),
    slo: float = typer.Option(0.999, "--slo", help="SLO target (e.g. 0.999 for 99.9%)"),
    window_days: int = typer.Option(28, "--window-days", help="Burn rate window"),
    budget_days: int = typer.Option(90, "--budget-days", help="Error budget period"),
    output: str = typer.Option("table", "--output", choices=["table", "json"]),
) -> None:
    """Compute SLO burn rates and error budgets."""
    console.print(f"[bold blue]Parsing[/] {input_path}...")

    df = parse_metrics(
        input_path, ts_col, latency_col, status_col, error_above, console
    )

    if df.empty:
        typer.echo("No valid data found.", err=True)
        raise typer.Exit(1)

    console.print("[bold blue]Computing[/] burn rates...")
    results = compute_burn_rates(df, metric, slo, window_days, budget_days)

    render_results(results, output, console)


if __name__ == "__main__":
    app()
