import click
from rich.console import Console
from .scanner import scan_requirements
from .formatters import format_output

console = Console()

@click.command()
@click.option('-r', '--requirements', type=click.Path(exists=True), required=True)
@click.option('--threshold', default=0.82, show_default=True)
@click.option('--format', 'fmt', default='text', type=click.Choice(['text', 'json', 'sarif']))
def cli(requirements, threshold, fmt):
    """Detect potential typosquatting in dependency files."""
    findings = scan_requirements(requirements, threshold)
    console.print(format_output(findings, fmt))