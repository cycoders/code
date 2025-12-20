import asyncio
import typer
from pathlib import Path
from typing import List

from rich.console import Console

from . import __version__
from .config import init_config, load_config, save_config
from .checker import check_endpoints
from .models import EndpointConfig, PulseConfig
from .reporter import render_report, render_trend
from .storage import Storage


app = typer.Typer(help="Pulse CLI: HTTP health monitoring", add_completion=False)
console = Console()
storage = Storage()


def parse_status_list(status_str: str) -> List[int]:
    return [int(s.strip()) for s in status_str.split(",") if s.strip()]


@app.command()
def version():
    """Show version."""
    console.print(f"[bold green]Pulse CLI v{__version__}[/]")


@app.command()
def init():
    """Init config dir/YAML."""
    init_config()


@app.command()
def add(
    name: str = typer.Option(..., "--name", help="Unique name"),
    url: str = typer.Option(..., "--url", help="Target URL"),
    expected_status: str = typer.Option("200", "--expected-status"),
    max_resp_time: float = typer.Option(500.0, "--max-resp-time"),
    content_match: str = typer.Option(None, "--content-match"),
    check_cert: bool = typer.Option(True, "--check-cert"),
):
    """Add endpoint to config."""
    ep = EndpointConfig(
        name=name,
        url=url,
        expected_status=parse_status_list(expected_status),
        max_resp_time=max_resp_time,
        content_match=content_match,
        check_cert=check_cert,
    )
    config = load_config()
    if any(e.name == name for e in config.endpoints):
        raise typer.BadParameter(f"'{name}' exists.")
    config.endpoints.append(ep)
    save_config(config)


@app.command()
def check(name: str = typer.Option(None, "--name")):
    """Run checks (all or named)."""
    config = load_config()
    endpoints = (
        [e for e in config.endpoints if e.name == name] if name else config.endpoints
    )
    if not endpoints:
        raise typer.BadParameter(f"No endpoints{name and f' '{name}' or 'configured'}. Run 'add'.")
    from rich.progress import Progress, SpinnerColumn, TextColumn

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
    ) as prog:
        task = prog.add_task("[cyan]Checking...", total=len(endpoints))
        results = asyncio.run(check_endpoints(endpoints, storage))
        prog.advance(task)
    render_report(results)


@app.command()
def report(name: str = typer.Option(None, "--name")):
    """Latest results table."""
    results = (
        storage.get_checks(name, 1) if name else storage.get_latest_per_endpoint()
    )
    if not results:
        console.print("[yellow]No data. Run 'check'.[/]")
        raise typer.Exit(1)
    render_report(results)


@app.command()
def trend(
    name: str,
    days: int = typer.Option(30, "--days"),
    metric: str = typer.Option("response_time_ms", "--metric"),
):
    """Trend view/sparkline."""
    checks = storage.get_checks(name, days=days)
    render_trend(checks, metric)


if __name__ == "__main__":
    app()