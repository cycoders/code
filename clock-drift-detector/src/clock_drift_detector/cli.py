import click
from rich.console import Console
from clock_drift_detector.analyzer import analyze
from clock_drift_detector.report import generate_report

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.argument('sources', nargs=-1, type=click.Path(exists=True))
@click.option('--key', default='trace_id', help='Correlation field')
@click.option('--ts-field', default='ts', help='Timestamp field name')
@click.option('--report', type=click.Path(), default='drift.html')
def analyze_cmd(sources, key, ts_field, report):
    results = analyze(sources, key, ts_field)
    generate_report(results, report)
    console.print(f"Report written to {report}")