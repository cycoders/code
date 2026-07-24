import click
from rich.console import Console
from numeric_tolerance_analyzer.analyzer import ToleranceAnalyzer

console = Console()

@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def main(paths):
    """Analyze numeric comparisons and suggest tolerances."""
    analyzer = ToleranceAnalyzer()
    for path in paths:
        console.print(f"Analyzing {path}...")
    console.print("Analysis complete.")