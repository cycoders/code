import click
from rich.console import Console
from .analyzer import TraceAnalyzer

console = Console()

@click.group()
def cli():
    """OpenTelemetry sampling strategy advisor"""
    pass

@cli.command()
@click.argument('trace_file', type=click.Path(exists=True))
@click.option('--strategy', default='adaptive', help='Sampling strategy')
@click.option('--budget', default=0.1, type=float, help='Target sampling budget')
def analyze(trace_file, strategy, budget):
    analyzer = TraceAnalyzer()
    result = analyzer.run(trace_file, strategy, budget)
    console.print(result)