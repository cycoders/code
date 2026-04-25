import typer
import yaml
from rich.console import Console
from rich_click import RichClickGroup
from .models import SimulationConfig
from .simulator import Simulator

console = Console()
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, rich_markup_mode="rich")
app = RichClickGroup(app, console=console)

@app.command(name="run")
def run_command(
    config_file: str = typer.Option(None, "--config", "-c", help="YAML config file"),
    rps: float = typer.Option(10.0, "--rps", "-r", min=0.1, help="Requests per second"),
    duration: int = typer.Option(60, "--duration", "-d", min=1, help="Simulation duration (secs)"),
    error_rate: float = typer.Option(0.1, "--error-rate", "-e", min=0, max=1, help="Service error rate"),
    ramp: float = typer.Option(0.0, "--ramp", min=0, help="Ramp duration (secs)"),
    output: str = typer.Option("console", "--output", "-o", help="Output: console|json|csv"),
):
    """
    Run circuit breaker simulation.
    """
    try:
        if config_file:
            with open(config_file) as f:
                data = yaml.safe_load(f)
            cfg = SimulationConfig.model_validate(data)
        else:
            cfg = SimulationConfig(
                rps=rps,
                duration_secs=duration,
                error_rate=error_rate,
                ramp_duration_secs=ramp,
            )
        console.print(f"[bold cyan]Starting sim[/]: {cfg.rps} RPS, {cfg.duration_secs}s, err={cfg.error_rate}")
        sim = Simulator(cfg, console)
        stats = sim.run(output)
        console.print(f"[green]✓ Complete: {sum(s.total_requests for s in stats.breakers.values())} reqs[/]")
    except FileNotFoundError:
        typer.echo(f"Error: Config file '{config_file}' not found.", err=True)
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
