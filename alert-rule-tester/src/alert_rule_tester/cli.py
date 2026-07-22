import click
from rich.console import Console
from .simulator import simulate

console = Console()

@click.command()
@click.argument("rules_dir", type=click.Path(exists=True))
@click.option("--metrics", required=True, type=click.Path(exists=True))
@click.option("--since", default="7d")
def cli(rules_dir, metrics, since):
    """Run alert rule simulation."""
    results = simulate(rules_dir, metrics, since)
    console.print(results)