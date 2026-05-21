import click
from rich.console import Console
from .core import analyze_hotspots

console = Console()

@click.command()
@click.option('--repo', default='.', help='Path to git repository')
@click.option('--since', default='365d', help='Git history window')
@click.option('--top', default=20, type=int, help='Number of results to show')
@click.option('--format', 'fmt', default='table', type=click.Choice(['table', 'json', 'csv']))
def main(repo, since, top, fmt):
    """Identify code hotspots by correlating complexity and churn."""
    results = analyze_hotspots(repo, since, top)
    if fmt == 'table':
        from .report import render_table
        render_table(results, console)
    elif fmt == 'json':
        import json
        console.print(json.dumps(results, indent=2))