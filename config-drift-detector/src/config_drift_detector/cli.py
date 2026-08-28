import click
from rich.console import Console
from config_drift_detector import compare, report

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.option('--baseline', required=True, type=click.Path(exists=True))
@click.option('--targets', required=True)
@click.option('--format', default='text', type=click.Choice(['text', 'sarif', 'json']))
def compare_cmd(baseline, targets, format):
    result = compare.run(baseline, targets.split(','))
    report.render(result, format, console)