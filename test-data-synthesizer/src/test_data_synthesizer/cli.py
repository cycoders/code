import click
from rich.console import Console

console = Console()

@click.group()
def main():
    """Schema-aware synthetic test data generator."""
    pass

@main.command()
@click.option('--schema', type=click.Path(exists=True), help='JSON Schema file')
@click.option('--rows', default=1000, show_default=True)
@click.option('--seed', default=42, show_default=True)
@click.option('--out', required=True, type=click.Path())
def generate(schema, rows, seed, out):
    console.print(f"Generating {rows} rows → {out}")