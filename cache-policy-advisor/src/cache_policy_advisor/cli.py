import click
from rich.console import Console
from cache_policy_advisor.analyzer import analyze_logs
from cache_policy_advisor.recommender import recommend
from cache_policy_advisor.models import LogFormat

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.argument('logfile', type=click.Path(exists=True))
@click.option('--format', 'fmt', type=click.Choice([e.value for e in LogFormat]), default='combined')
@click.option('--window', default='7d')
def analyze(logfile, fmt, window):
    result = analyze_logs(logfile, LogFormat(fmt), window)
    console.print(result)