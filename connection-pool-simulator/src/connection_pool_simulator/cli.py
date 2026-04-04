import asyncio
import json
import sys
import typing as t
from pathlib import Path
from typing import Optional

import typer
import rich.console
import rich.progress
import rich.status
import rich.table
from rich import box

from .config import SimConfig, get_config
from .simulator import run_simulation


app = typer.Typer(help="Connection Pool Simulator: Tune pools offline.")
console = rich.console.Console()


@app.command(help="Simulate single pool config")
def simulate(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="YAML config file"
    ),
    max_size: Optional[int] = typer.Option(None, "--max-size"),
    acquire_timeout: Optional[float] = typer.Option(None, "--acquire-timeout"),
    num_clients: Optional[int] = typer.Option(None, "--num-clients"),
    requests_per_client: Optional[int] = typer.Option(None, "--requests-per-client"),
    query_duration_mean: Optional[float] = typer.Option(None, "--query-duration-mean"),
    query_duration_std: Optional[float] = typer.Option(None, "--query-duration-std"),
    ramp_up_duration: Optional[float] = typer.Option(None, "--ramp-up-duration"),
    output: t.Literal["table", "json"] = typer.Option("table", "--output"),
):
    try:
        cfg = get_config(
            config_file,
            max_size=max_size,
            acquire_timeout=acquire_timeout,
            num_clients=num_clients,
            requests_per_client=requests_per_client,
            query_duration_mean=query_duration_mean,
            query_duration_std=query_duration_std,
            ramp_up_duration=ramp_up_duration,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)

    with console.status("[bold green]Simulating pool behavior..."):
        metrics = asyncio.run(run_simulation(cfg))

    if output == "json":
        print(json.dumps(metrics, indent=2))
    else:
        table = rich.table.Table(box=box.ROUNDED, title="[bold]Pool Simulation Results[/bold]")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        table.add_row("Throughput (req/s)", f"{metrics['throughput']:.1f}")
        table.add_row("Utilization %", f"{metrics['utilization_pct']:.1f}")
        table.add_row("Reject rate %", f"{metrics['reject_rate_pct']:.2f}")
        table.add_row("P95 wait time", f"{metrics['p95_wait_time']:.3f}s")
        table.add_row("Avg wait time", f"{metrics['avg_wait_time']:.3f}s")
        table.add_row("Avg query time", f"{metrics['avg_query_time']:.3f}s")
        table.add_row("Total time", f"{metrics['total_time']:.2f}s")
        table.add_row("Successful / Total", f"{metrics['successful']} / {metrics['total_requests']}")
        console.print(table)


@app.command(help="Sweep max_sizes, recommend optimal config")
def recommend(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="YAML config file (base params)"
    ),
    target_throughput: Optional[float] = typer.Option(None, "--target-throughput"),
    max_size_start: int = typer.Option(1, "--max-size-start"),
    max_size_step: int = typer.Option(5, "--max-size-step"),
    max_size_max: int = typer.Option(100, "--max-size-max"),
    acquire_timeout: Optional[float] = typer.Option(None, "--acquire-timeout"),
    num_clients: Optional[int] = typer.Option(None, "--num-clients"),
    requests_per_client: Optional[int] = typer.Option(None, "--requests-per-client"),
    query_duration_mean: Optional[float] = typer.Option(None, "--query-duration-mean"),
    query_duration_std: Optional[float] = typer.Option(None, "--query-duration-std"),
    ramp_up_duration: Optional[float] = typer.Option(None, "--ramp-up-duration"),
):
    try:
        # Get base config (dummy max_size)
        base_cfg = get_config(
            config_file,
            max_size=1,  # dummy
            acquire_timeout=acquire_timeout,
            num_clients=num_clients,
            requests_per_client=requests_per_client,
            query_duration_mean=query_duration_mean,
            query_duration_std=query_duration_std,
            ramp_up_duration=ramp_up_duration,
        )
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1)

    sizes = list(range(max_size_start, max_size_max + 1, max_size_step))
    results: list[Dict[str, Any]] = []

    with rich.progress.Progress() as progress:
        task = progress.add_task("[green]Running simulations...", total=len(sizes))
        for ms in sizes:
            sim_cfg = base_cfg.model_copy(update={"max_size": ms})
            metrics = asyncio.run(run_simulation(sim_cfg))
            results.append({"max_size": ms, **metrics})
            progress.advance(task)

    # Find best
    best: Optional[Dict[str, Any]] = None
    for res in results:
        if res["reject_rate_pct"] < 1.0 and res["utilization_pct"] < 90.0:
            if best is None or res["throughput"] > best["throughput"]:
                best = res

    # Table
    table = rich.table.Table(box=box.ROUNDED, title="[bold]Recommendation Sweep[/bold]")
    table.add_column("Max Size", style="cyan")
    table.add_column("Throughput", justify="right")
    table.add_column("Util %", justify="right")
    table.add_column("Reject %", justify="right")
    table.add_column("P95 Wait", justify="right")

    for res in results:
        marker = " ⭐" if res is best else ""
        table.add_row(
            f"{res['max_size']}{marker}",
            f"{res['throughput']:.1f}",
            f"{res['utilization_pct']:.1f}",
            f"{res['reject_rate_pct']:.2f}",
            f"{res['p95_wait_time']:.3f}s",
        )

    console.print(table)

    if best:
        console.print(
            f"\n[bold green]RECOMMENDED:[/bold] max_size={best['max_size']}, throughput={best['throughput']:.1f} req/s, util={best['utilization_pct']:.1f}%"
        )
        if target_throughput and best["throughput"] < target_throughput:
            console.print("[yellow]Note: Below target throughput.[/yellow]")
    else:
        console.print("[red]No optimal config found (all >1% rejects or >90% util). Increase max_size_max.[/red]")


if __name__ == "__main__":
    app()
