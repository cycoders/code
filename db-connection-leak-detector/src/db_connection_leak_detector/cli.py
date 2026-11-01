import click
from rich.console import Console
from .scanner import scan_path

console = Console()

@click.group()
def main():
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
def scan(path):
    """Run static analysis on a directory or file."""
    findings = scan_path(path)
    for f in findings:
        console.print(f"[red]{f}")
    raise SystemExit(1 if findings else 0)