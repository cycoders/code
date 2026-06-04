import click
from rich.console import Console
from .core import correlate
from .parser import parse_logs

console = Console()

@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--keys", default="trace_id", help="Comma-separated join keys")
@click.option("--window", default="5s", help="Temporal correlation window")
@click.option("--format", default="text", type=click.Choice(["text", "json"]))
def main(files, keys, window, format):
    """Correlate events across log sources."""
    events = parse_logs(files or ["-"])
    chains = correlate(events, keys.split(","), window)
    if format == "json":
        console.print_json(data=chains)
    else:
        for chain in chains:
            console.print(chain)