import json
import typer
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.progress import track

import rollout_simulator
from .parser import parse_metrics, group_by_deploy
from .simulator import run_simulation
from .strategies import get_strategy_steps
from .sample import generate_sample
from .types import SimResult


app = typer.Typer(add_completion=False)
console = Console()


def show_results(results: List[SimResult], threshold: float):
    """Display rich results table and recommendation."""
    table = Table(title=f"Rollout Risks (threshold={threshold:.1%})")
    table.add_column("Strategy", style="cyan", no_wrap=True)
    table.add_column("Risk %", justify="right")
    table.add_column("P95 Max Error", justify="right")
    table.add_column("Steps")

    for r in results:
        table.add_row(
            r.strategy_name,
            f"{r.risk_pct:.1f}%",
            f"{r.p95_max_error:.4f}",
            ",".join(str(s) for s in r.steps),
        )

    console.print(table)

    if results:
        best = min(results, key=lambda r: r.risk_pct)
        console.print(
            f"\n[bold green]Recommended: {best.strategy_name} "
            f"(risk: {best.risk_pct:.1f}%)[/bold green]"
        )


@app.command()
def analyze(
    metrics_file: Path = typer.Argument(..., exists=True, readable=True),
    threshold: float = typer.Option(0.02, "--threshold/-t", min=0.0, max=1.0),
    sims: int = typer.Option(1000, "--sims/-s", min=10, max=100000),
    strategies: List[str] = typer.Option(
        ["canary-conservative", "canary-aggressive", "big-bang"],
        "--strategy/-S",
    ),
):
    """Simulate rollouts from metrics.jsonl."""
    try:
        entries = parse_metrics(metrics_file)
        deploys = group_by_deploy(entries)
        console.print(
            f"[green]✓ Loaded {len(entries)} metrics across "
            f"{len(deploys)} deploys (baseline: {deploys[-1].avg_error_rate:.4f}).[/green]"
        )

        strats = [(name, get_strategy_steps(name)) for name in strategies]
        results = []
        for name, steps in track(strats, description="Simulating..."):
            result = run_simulation(deploys, steps, name, threshold, sims)
            results.append(result)

        show_results(results, threshold)
    except Exception as e:
        console.print(f"[red bold]Error:[/red bold] {str(e)}")
        raise typer.Exit(code=1) from e


@app.command()
def generate_sample(output: Path = typer.Argument(Path("sample-metrics.jsonl"))):
    """Generate example metrics.jsonl (4 deploys, realistic deltas)."""
    try:
        sample_data = generate_sample()
        output.write_text(sample_data)
        console.print(f"[green]✓ Wrote {len(sample_data.splitlines())} lines to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error writing sample: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()