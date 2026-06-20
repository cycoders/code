import click
from rich.console import Console
from .parser import parse_file
from .stats import compare

console = Console()

@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--threshold', default=0.05, help='Significance threshold')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'csv']))
def cli(files, threshold, output_format):
    """Statistical benchmark comparison"""
    if len(files) < 2:
        raise click.UsageError("Provide at least two benchmark files")
    results = [parse_file(f) for f in files]
    report = compare(results, threshold)
    if output_format == 'table':
        console.print(report)
    else:
        click.echo(report)