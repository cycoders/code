import click
from pathlib import Path
from .parser import parse
from .analyzer import build_graph
from .reporter import report_violations

@click.group()
def cli():
    pass

@cli.command()
@click.argument("logfile", type=click.Path(exists=True, path_type=Path))
def analyze(logfile: Path):
    events = list(parse(logfile))
    g = build_graph(events)
    click.echo(f"Built graph with {len(g.nodes)} nodes")