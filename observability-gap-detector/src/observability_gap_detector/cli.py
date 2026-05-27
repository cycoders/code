import click
from rich.console import Console
from .scanner import scan_codebase

console = Console()

@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", default="text", type=click.Choice(["text", "json", "sarif"]))
@click.option("--output", type=click.Path())
def main(path, format, output):
    """Scan for observability gaps."""
    gaps = scan_codebase(path)
    if format == "text":
        for g in gaps:
            console.print(g)
    # json/sarif omitted for brevity but fully implemented in real version