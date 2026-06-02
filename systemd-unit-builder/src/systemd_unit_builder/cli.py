import click, yaml
from rich.console import Console
from .validator import validate_config
from .hardener import apply_hardening
from .renderer import render_unit

console = Console()

@click.command()
@click.option("--config", required=True, type=click.Path(exists=True))
@click.option("--out", default="-", type=click.File("w"))
def main(config, out):
    """Generate hardened systemd unit file."""
    with open(config) as f:
        data = yaml.safe_load(f)
    cfg = validate_config(data)
    hardened = apply_hardening(cfg)
    unit = render_unit(hardened)
    out.write(unit)
    console.print("[green]Unit generated successfully[/green]")