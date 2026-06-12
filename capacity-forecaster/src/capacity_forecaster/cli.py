import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """Capacity forecasting CLI"""
    pass

@cli.command()
@click.option('--input', required=True, type=click.Path(exists=True))
@click.option('--horizon', default='90d')
@click.option('--model', default='seasonal', type=click.Choice(['linear', 'exponential', 'seasonal']))
def forecast(input, horizon, model):
    console.print(f"[bold green]Running {model} forecast on {input} for {horizon}[/]")