from __future__ import annotations

import click
from rich.console import Console

from .validator import validate

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True))
def main(path: str) -> None:
    errors = validate(path)
    if errors:
        for e in errors:
            console.print(f"[red]✗[/red] {e}")
        raise SystemExit(1)
    console.print("[green]✓[/green] pyproject.toml is valid")