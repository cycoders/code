import typer
from typing import Optional, List
from pathlib import Path

from .manager import (
    up,
    down,
    status,
    logs,
    print_env,
    connect,
    get_effective_services,
)
from .config import write_sample_config

app = typer.Typer(add_completion=False)

@app.command(help="Bring up services (default: all enabled)")
def up_cmd(
    services: Optional[List[str]] = typer.Argument(None, metavar="[SERVICE]"),
):
    up(services)

@app.command(help="Bring down services")
def down_cmd(
    services: Optional[List[str]] = typer.Argument(None, metavar="[SERVICE]"),
):
    down(services)

@app.command(help="Show status table (--live for dashboard)")
def status_cmd(live: bool = typer.Option(False, "--live", help="Live refresh")):
    status(live)

@app.command(help="Tail logs")
def logs_cmd(
    service: str,
    follow: bool = typer.Option(True, "-f", "Follow logs"),
    tail: Optional[int] = typer.Option(None, "--tail"),
):
    logs(service, follow, tail)

@app.command(help="Print connection/env strings")
def env_cmd(service: str):
    print_env(service)

@app.command(help="Connect to service shell/DB")
def connect_cmd(service: str):
    connect(service)

@app.command(help="List available services")
def list_cmd():
    effective = get_effective_services()
    console = typer.console
    console.print("[bold cyan]Available services:[/]")
    for svc in sorted(effective):
        console.print(f"  [green]{svc}[/]")

@app.command(help="Init sample config.toml")
def config_cmd_init():
    write_sample_config()

if __name__ == "__main__":
    app()
