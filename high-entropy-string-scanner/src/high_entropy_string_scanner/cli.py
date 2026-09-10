import click
from .scanner import scan_path

@click.group()
def cli():
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--min-entropy', default=4.5, show_default=True)
@click.option('--format', 'fmt', default='text', type=click.Choice(['text','json','sarif']))
def scan(path, min_entropy, fmt):
    """Scan path for high-entropy strings."""
    findings = scan_path(path, min_entropy)
    click.echo(f"Found {len(findings)} potential secrets")