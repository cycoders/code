import typer
import yaml
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown

from .config import Config
from .simulator import run_simulation
from .renderer import render_results, render_live


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def sim(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="YAML config file"),
    duration: Optional[float] = typer.Option(None, "--duration", "-d", help="Simulation duration (s)"),
    arrival_rate: Optional[float] = typer.Option(None, "--arrival-rate", "-r", help="Req/s (Poisson)"),
    output: str = typer.Option("live", "--output", "-o", help="live|table|json"),
    seed: Optional[int] = typer.Option(None, "--seed", "-s", help="Random seed"),
):
    """Run load balancer simulation."""

    cfg_dict = {}
    if config_path:
        try:
            with open(config_path) as f:
                cfg_dict = yaml.safe_load(f)
        except Exception as e:
            typer.echo(f"Error loading config: {e}", err=True)
            raise typer.Exit(1)

    cfg = Config.model_validate(cfg_dict)

    # CLI overrides
    if duration is not None:
        cfg.duration = duration
    if arrival_rate is not None:
        cfg.arrival_rate = arrival_rate
    if seed is not None:
        cfg.seed = seed

    # Validate
    cfg.model_validate(cfg)

    console.print(f"[bold green]Simulating {cfg.strategy.upper()} for {cfg.duration}s @ {cfg.arrival_rate} rps...[/]")

    results = run_simulation(cfg)

    if output == "live":
        render_live(results)
    elif output == "table":
        render_results(results, console)
    elif output == "json":
        import json
        console.print(json.dumps(results, indent=2))
    else:
        typer.echo("Invalid output", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()