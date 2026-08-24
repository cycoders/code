import click
from rich.console import Console
from .scanner import scan

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--lockfile', type=click.Path(exists=True))
@click.option('--sbom', type=click.Path(exists=True))
@click.option('--policy', type=click.Path(exists=True))
@click.option('--format', 'fmt', default='markdown', type=click.Choice(['json','sarif','markdown']))
def scan_cmd(lockfile, sbom, policy, fmt):
    report = scan(lockfile, sbom, policy)
    if fmt == 'json':
        console.print_json(data=report)
    elif fmt == 'sarif':
        console.print(report['sarif'])
    else:
        console.print(report['markdown'])