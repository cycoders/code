import click
from rich.console import Console
from .core import GilMonitor

console = Console()

@click.command()
@click.option("--duration", default=10, help="Seconds to monitor")
def main(duration: int) -> None:
    monitor = GilMonitor()
    with monitor.measure():
        import time; time.sleep(duration)
    console.print("[green]GIL contention report generated[/green]")