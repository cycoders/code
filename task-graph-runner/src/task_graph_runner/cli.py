import click
from pathlib import Path
from .parser import load_graph

@click.group()
def main():
    pass

@main.command()
@click.argument('graph', type=click.Path(exists=True))
def run(graph):
    g = load_graph(Path(graph))
    click.echo(f"Loaded {len(g.tasks)} tasks")