import typer
from typing import Optional

from rich.console import Console

import leader_election_simulator
from leader_election_simulator.simulator import Simulator
from leader_election_simulator.viz import run_live_sim

app = typer.Typer()
console = Console()

@app.command(help="Run Raft leader election simulation (TUI or batch)")
def run(
    num_nodes: int = typer.Argument(5, min=3, max=15, help="Number of nodes"),
    duration: int = typer.Option(1000, "--duration", help="Ticks to simulate"),
    tick_delay: float = typer.Option(0.02, "--tick-delay", help="Seconds per tick (realtime)"),
    heartbeat_interval: int = typer.Option(100, "--heartbeat-interval", help="Ticks between heartbeats"),
    election_timeout_min: int = typer.Option(250, "--election-timeout-min"),
    election_timeout_max: int = typer.Option(500, "--election-timeout-max"),
    failure_prob: float = typer.Option(0.001, "--failure-prob", help="Prob node fails per tick"),
    recovery_prob: float = typer.Option(0.1, "--recovery-prob"),
    partition_prob: float = typer.Option(0.001, "--partition-prob", help="Prob partition change"),
    seed: int = typer.Option(42, "--seed"),
    realtime: bool = typer.Option(True, "--realtime"),
    output: Optional[str] = typer.Option(None, "--output", help="Export history JSON"),
):
    typer.echo("🚀 Starting Leader Election Simulator", err=True)

    sim = Simulator(
        num_nodes=num_nodes,
        seed=seed,
        heartbeat_interval=heartbeat_interval,
        election_timeout_min=election_timeout_min,
        election_timeout_max=election_timeout_max,
        failure_prob=failure_prob,
        recovery_prob=recovery_prob,
        partition_prob=partition_prob,
    )

    try:
        if realtime:
            run_live_sim(sim, duration, tick_delay)
        else:
            sim.run(duration)
            if output:
                sim.export(output)
                typer.echo(f"📤 History exported to {output}")
        sim.print_summary(console)
    except KeyboardInterrupt:
        typer.echo("\n⏹️  Simulation interrupted")
        sim.print_summary(console)

if __name__ == "__main__":
    app()