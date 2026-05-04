import typer
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models import SimConfig, aggregate_metrics, percentile
from .simulator import run_simulation
from .visualizer import plot_simulation, plot_comparison


app = typer.Typer(add_completion=False)
console = Console()


def print_metrics_table(metrics: "Metrics"):
    table = Table(title=f"[bold cyan]{metrics.name or metrics.backoff.strategy.title()}[/bold cyan]")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="magenta")

    table.add_row("Success Rate", f"{metrics.success_rate:.1%}")
    table.add_row("Avg Attempts", f"{metrics.avg_attempts:.2f}")
    table.add_row("P50 Attempts", f"{metrics.p50_attempts:.2f}")
    table.add_row("P95 Attempts", f"{metrics.p95_attempts:.2f}")
    table.add_row("Avg Time (s)", f"{metrics.avg_time:.3f}")
    table.add_row("P50 Time (s)", f"{metrics.p50_time:.3f}")
    table.add_row("P95 Time (s)", f"{metrics.p95_time:.3f}")
    table.add_row("Max Time (s)", f"{metrics.max_time:.3f}")

    console.print(table)


def print_comparison_table(metrics_list: list):
    table = Table(title="[bold green]Comparison[/bold green]")
    table.add_column("Strategy", style="cyan")
    for m in metrics_list:
        table.add_column(m.name, justify="right")

    # Headers done, rows
    rows = [
        ("Success Rate", *[f"{m.success_rate:.1%}" for m in metrics_list]),
        ("Avg Attempts", *[f"{m.avg_attempts:.2f}" for m in metrics_list]),
        ("P95 Attempts", *[f"{m.p95_attempts:.2f}" for m in metrics_list]),
        ("P95 Time (s)", *[f"{m.p95_time:.3f}" for m in metrics_list]),
    ]
    for row in rows:
        table.add_row(*row)

    console.print(table)


@app.command(help="Simulate a single config")
def simulate(
    config_path: Path = typer.Argument(..., exists=True, help="YAML config path"),
    seed: int = typer.Option(42, "--seed"),
    plot: bool = typer.Option(True, "--plot"),
    output: Path = typer.Option("simulation.png", "--output", help="Plot file"),
):
    try:
        with open(config_path) as f:
            cfg_dict = yaml.safe_load(f)
        cfg = SimConfig.model_validate(cfg_dict)
        cfg.seed = seed

        rprint(f"[bold blue]🔄 Simulating {cfg.num_trials:,} trials with [magenta]{cfg.backoff.strategy}[/][/bold blue]")

        results = run_simulation(cfg)
        metrics = aggregate_metrics(results, str(config_path.stem))

        print_metrics_table(metrics)

        if plot:
            plot_simulation(results, output)
            rprint(f"[bold green]✅ Plot saved to {output}[/]")

    except Exception as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1)


@app.command(help="Compare multiple configs")
def compare(
    config_paths: List[Path] = typer.Argument(..., exists=True, help="YAML config paths"),
    output: Path = typer.Option("comparison.png", "--output"),
):
    if len(config_paths) > 6:
        raise typer.BadParameter("Max 6 configs for comparison")

    all_metrics = []
    for i, path in enumerate(config_paths):
        with open(path) as f:
            cfg_dict = yaml.safe_load(f)
        cfg = SimConfig.model_validate(cfg_dict)
        results = run_simulation(cfg)
        metrics = aggregate_metrics(results, path.stem)
        all_metrics.append(metrics)

    print_comparison_table(all_metrics)
    plot_comparison(all_metrics, output)
    rprint(f"[bold green]✅ Comparison plot saved to {output}[/]")


if __name__ == "__main__":
    app()
