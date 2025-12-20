import asyncio
import os
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live

from .proxy import create_record_app, create_replay_app, run_proxy

cli = typer.Typer(no_args_is_help=True)
console = Console()

@cli.command()
def record(
    upstream: str = typer.Option(..., "--upstream", "-u", help="Upstream base URL"),
    cassette: Path = typer.Option("cassettes/default.yaml", "--cassette", "-c", exists=False),
    port: int = typer.Option(8080, "--port", "-p"),
    host: str = typer.Option("127.0.0.1", "--host"),
):
    """Record mode: proxy to upstream, save to cassette."""
    console.print(f"[bold green]RECORD[/bold green] {host}:{port} -> {upstream} | cassette: {cassette}")
    async def app_factory():
        return create_record_app(str(upstream), str(cassette))
    asyncio.run(run_proxy(host, port, app_factory))

@cli.command()
def replay(
    cassette: Path = typer.Option(..., "--cassette", "-c", exists=True),
    port: int = typer.Option(8080, "--port", "-p"),
    host: str = typer.Option("127.0.0.1", "--host"),
    jitter: float = typer.Option(0.0, "--jitter", "-j", help="Latency jitter factor (0.2=±20%)"),
    error_rate: float = typer.Option(0.0, "--error-rate", "-e", help="Simulated error probability"),
):
    """Replay mode: serve from cassette."""
    console.print(f"[bold blue]REPLAY[/bold blue] {host}:{port} <- {cassette} | jitter:{jitter} error:{error_rate}")
    async def app_factory():
        return create_replay_app(str(cassette), jitter, error_rate)
    asyncio.run(run_proxy(host, port, app_factory))

if __name__ == "__main__":
    cli()
