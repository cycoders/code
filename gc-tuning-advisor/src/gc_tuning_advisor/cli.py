import click
from rich.console import Console
from .parser import parse_gc_log
from .analyzer import analyze
from .recommender import recommend

console = Console()

@click.group()
def main(): pass

@main.command()
@click.argument('logfile', type=click.File())
def analyze_cmd(logfile):
    events = parse_gc_log(logfile)
    result = analyze(events)
    rec = recommend(result)
    console.print(f"Recommended thresholds: {rec}")