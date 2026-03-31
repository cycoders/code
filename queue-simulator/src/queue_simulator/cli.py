import json
import typer
from pathlib import Path
from typing import Optional

import queue_simulator.types as types
import queue_simulator.simulator as sim_mod
import queue_simulator.visualizer as viz
import queue_simulator.distributions as dists

app = typer.Typer(no_args_is_help=True)

@app.command(name="sim")
def simulate(  # noqa: PLR0913
    sim_duration: float = typer.Argument(..., ge=1.0, help="Simulation duration (seconds)"),
    arrival_rate: float = typer.Argument(..., ge=0.0, help="Poisson arrival rate (jobs/second)"),
    num_workers: int = typer.Option(1, "--workers", "-w", min=1, help="Number of parallel workers"),
    service_dist: str = typer.Option("fixed", "--dist", help="Service time dist: fixed|exp|empirical"),
    service_mean: float = typer.Option(0.1, "--service-mean", "-m", ge=0.001, help="Mean service time (s) for fixed/exp"),
    service_file: Optional[Path] = typer.Option(None, "--service-file", "-f", help="CSV for empirical dist"),
    seed: Optional[int] = typer.Option(None, "--seed", "-s", help="RNG seed for reproducibility"),
    output: str = typer.Option("table", "--output", "-o", help="Output: table|plot|json|all"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="JSON config file (CLI overrides)"),
):
    "Run job queue simulation."

    # Load config if provided
    params = {
        "service_mean": service_mean,
        "service_file": service_file,
    }
    if config:
        try:
            cfg = json.loads(config.read_text())
            params.update(cfg)
        except Exception as e:
            typer.echo(f"[red]Config error: {e}[/red]", err=True)
            raise typer.Exit(1)

    # Validate empirical
    if service_dist == "empirical":
        if not params["service_file"]:
            raise typer.BadParameter("--service-file required for empirical")
        service_file = Path(params["service_file"])
    else:
        service_file = None

    # Build sampler
    sampler_params = {"service_mean": params["service_mean"], "service_file": service_file}
    try:
        service_sampler = dists.get_service_sampler(service_dist, sampler_params, random.Random())
    except Exception as e:
        raise typer.BadParameter(str(e))

    # Run sim
    typer.echo(f"[green]Simulating {sim_duration}s @ {arrival_rate} jobs/s, {num_workers} workers ({service_dist} dist)[/green]")
    simulator = sim_mod.Simulator(num_workers, service_sampler)
    stats = simulator.run(sim_duration, arrival_rate, seed)

    # Output
    viz.show_output(stats, output)

if __name__ == "__main__":
    app()