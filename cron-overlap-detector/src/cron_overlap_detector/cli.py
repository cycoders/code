import click
from rich.console import Console

console = Console()

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--horizon-days', default=7)
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
def main(paths, horizon_days, format):
    """Detect cron execution overlaps."""
    console.print("[bold]cron-overlap-detector[/bold] v0.1.0")