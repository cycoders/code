import click
from rich.console import Console
from rich.table import Table

from .calculator import remaining_budget, burn_rate, hours_to_exhaustion

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option("--target", type=float, default=99.9)
@click.option("--total", type=int, required=True)
@click.option("--bad", type=int, required=True)
def compute(target, total, bad):
    rem = remaining_budget(target, total, bad)
    console.print(f"Remaining error budget: {rem:.0f} requests")