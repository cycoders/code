import click
from rich.console import Console
from .analyzer import analyze_project

console = Console()

@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', type=click.Path(), help='Path to config file')
@click.option('--format', 'fmt', default='text', type=click.Choice(['text','json']))
def main(path, config, fmt):
    """Detect missing deadline propagation."""
    findings = analyze_project(path, config)
    if fmt == 'json':
        import json
        console.print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            console.print(f"[red]MISSING[/red] {f['function']} at {f['location']}")