import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """Latency budget allocator CLI"""
    pass

@cli.command()
@click.option('--graph', required=True, type=click.Path(exists=True))
@click.option('--slo', required=True, help='Target p99 SLO (e.g. 250ms)')
@click.option('--output', required=True, type=click.Path())
def allocate(graph, slo, output):
    """Allocate per-hop budgets."""
    console.print(f"[green]Allocating budgets for SLO {slo} from {graph}[/green]")
    # Implementation would call core allocator here