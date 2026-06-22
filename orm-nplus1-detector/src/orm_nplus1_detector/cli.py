import click
from rich.console import Console

console = Console()

@click.group()
def main():
    """N+1 query detector CLI"""
    pass

@main.command()
@click.argument('path')
def scan(path):
    console.print(f'Scanning {path}...')