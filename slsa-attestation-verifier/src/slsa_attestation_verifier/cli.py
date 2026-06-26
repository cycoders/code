import click
from rich.console import Console
from .verifier import verify_attestation
from .policy import load_policy, evaluate

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--attestation', required=True, type=click.Path(exists=True))
@click.option('--artifact', required=True)
@click.option('--config', type=click.Path(exists=True))
def verify(attestation, artifact, config):
    policy = load_policy(config) if config else None
    result = verify_attestation(attestation, artifact, policy)
    if result.valid:
        console.print("[green]✓ Attestation valid[/green]")
    else:
        console.print(f"[red]✗ {result.reason}[/red]")
        raise click.Abort()
