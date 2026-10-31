import click
from rich.console import Console
from .histogram import HDRHistogram

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--input', type=click.File('r'), default='-')
@click.option('--output', type=click.Path(), required=True)
def record(input, output):
    h = HDRHistogram()
    for line in input:
        try:
            v = int(line.strip())
            h.record(v)
        except ValueError:
            continue
    console.print(f"Recorded {h.counts.sum()} samples")