import click
from rich.console import Console
from .analyzer import analyze_migrations

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--schema', type=click.Path(exists=True))
@click.option('--dialect', default='postgres')
def analyze(path, schema, dialect):
    results = analyze_migrations(path, schema, dialect)
    console.print(results)