import click
from rich.console import Console
from .validator import validate_stream
from .reporter import Reporter

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.option('--schema', required=True, type=click.Path(exists=True))
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def validate(schema, files):
    reporter = Reporter()
    for path in files:
        with open(path) as f:
            errors = validate_stream(f, schema)
            reporter.add(path, errors)
    reporter.print()
    if reporter.has_errors:
        raise SystemExit(1)