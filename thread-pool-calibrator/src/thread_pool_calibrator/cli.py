import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--workload', type=click.Path(exists=True), required=True)
def calibrate(workload):
    console.print(f"Calibrating from {workload}")