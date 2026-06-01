import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .validator import validate_env, ValidationError

console = Console()

@click.group()
def cli() -> None:
    pass

@cli.command()
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--schema", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--strict/--no-strict", default=True)
def validate(env_file: Path, schema: Path, strict: bool) -> None:
    try:
        errors = validate_env(env_file, schema, strict)
        if not errors:
            console.print("[green]Validation passed[/green]")
            return
        table = Table(title="Validation Errors")
        table.add_column("Line")
        table.add_column("Key")
        table.add_column("Error")
        for e in errors:
            table.add_row(str(e.get("line", "-")), str(e.get("path", ["-"])[0]), e["message"])
        console.print(table)
        raise click.ClickException("Validation failed")
    except ValidationError as exc:
        console.print(f"[red]{exc}[/red]")
        raise click.Abort()