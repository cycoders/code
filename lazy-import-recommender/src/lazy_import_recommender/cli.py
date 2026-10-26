import click
from rich.console import Console
from .scanner import scan_project
from .applier import apply_changes

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
def scan(path):
    results = scan_project(path)
    for r in results:
        console.print(r)

@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--apply', is_flag=True)
def apply(path, apply):
    apply_changes(path, apply)