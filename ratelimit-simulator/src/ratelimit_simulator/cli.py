import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

import ratelimit_simulator  # noqa
from .simulator import SimulationConfig, run_simulation
from .ui import RateLimitApp


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command(help="Interactive TUI simulator")
def tui():
    """Launch the TUI."""
    RateLimitApp().run()


@app.command(help="Run non-interactive simulation")
def simulate(
    policy: str = typer.Argument(..., help="Policy: fixed, sliding, token, leaky"),
    limit: int = typer.Option(100, "-l", "--limit", help="Limit/capacity"),
    window: Optional[float] = typer.Option(60.0, "-w", "--window", help="Window (s)"),
    refill_rate: Optional[float] = typer.Option(None, "-r", "--refill-rate", help="Token refill rate"),
    leak_rate: Optional[float] = typer.Option(None, "--leak-rate", help="Leaky rate"),
    rps: float = typer.Option(10.0, "--rps", help="Avg requests/sec"),
    duration: float = typer.Option(60.0, "-d", "--duration", help="Sim duration (s)"),
    num_keys: int = typer.Option(5, "-k", "--num-keys", help="Number of keys (users)"),
    burst_prob: float = typer.Option(0.1, "--burst-prob", help="Burst probability"),
):
    params = {"limit": limit}
    if window is not None:
        params["window"] = window
    p_lower = policy.lower()
    if p_lower in ("token", "leaky"):
        rate = refill_rate or leak_rate or (limit / (window or 60))
        params["capacity"] = limit
        key = "refill_rate" if p_lower == "token" else "leak_rate"
        params[key] = rate

    config = SimulationConfig(
        policy_name=p_lower,
        policy_params=params,
        rps=rps,
        duration=duration,
        num_keys=num_keys,
        burst_prob=burst_prob,
    )
    stats = run_simulation(config)

    table = Table(title=f"{policy.title()} Simulation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Hit Rate", f"{stats.hit_rate:.1%}")
    table.add_row("Total Requests", str(stats.total_requests))
    table.add_row("Accepted", str(stats.accepted))
    table.add_row("Rejected", str(stats.rejected))
    table.add_row("Max Burst", str(stats.max_burst))
    console.print(table)


def main():
    if __name__ == "__main__":
        app()
    app(prog_name="ratelimit-simulator")
