import click
from rich.console import Console
from .simulator import Simulator

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--nodes', default=5, help='Number of nodes')
@click.option('--vnodes', default=128, help='Virtual nodes per physical node')
@click.option('--keys', default=10000, help='Number of keys to place')
def run(nodes, vnodes, keys):
    sim = Simulator(nodes, vnodes, keys)
    dist = sim.run()
    console.print(dist)