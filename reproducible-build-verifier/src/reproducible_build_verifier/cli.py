import click
from rich.console import Console
from .analyzer import BuildAnalyzer
from .reporter import report

console = Console()

@click.group()
def cli():
    """Detect sources of build non-determinism."""
    pass

@cli.command()
@click.argument('left', type=click.Path(exists=True))
@click.argument('right', type=click.Path(exists=True))
@click.option('--format', default='rich', type=click.Choice(['rich', 'json']))
def compare(left, right, format):
    """Compare two build artifacts or manifests."""
    analyzer = BuildAnalyzer()
    findings = analyzer.analyze(left, right)
    report(findings, format, console)