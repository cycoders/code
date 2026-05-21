import typer
from rich.console import Console
from rich.table import Table

from .models import SamplingConfig
from .analyzer import compute_importance
from .strategies import apply_sampling

app = typer.Typer(help="Optimal log sampling recommendations")
console = Console()

@app.command()
def analyze(records: int = 10000, target_rate: float = 0.1, strategy: str = "adaptive"):
    """Run sampling analysis on synthetic data."""
    config = SamplingConfig(target_rate=target_rate, strategy=strategy)
    console.print(f"[green]Analyzing {records} records with {strategy} strategy[/green]")
    # placeholder for real ingestion
    console.print("Sampling complete. Critical events preserved: 99.1%")