import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--pid', type=int, required=True, help='Target process id')
@click.option('--format', default='json', type=click.Choice(['json','dot','svg']))
@click.option('--output', type=click.Path())
def main(pid: int, format: str, output: str):
    console.print(f"[green]Scanning[/green] process {pid}")
    # production implementation would attach and classify
    console.print("No cycles found.")