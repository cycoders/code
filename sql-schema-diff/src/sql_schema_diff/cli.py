import typer
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich_click import RichClickGroup

from .parser import parse_schema
from .differ import diff_schemas
from .render import render_diff


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
app = RichClickGroup(app, fallback=app)
console = Console()


@app.command(name="diff")
def diff_command(
    old_file: Path = typer.Argument(..., help="Path to old schema SQL file"),
    new_file: Path = typer.Argument(..., help="Path to new schema SQL file"),
    dialect: str = typer.Option("postgres", "--dialect", help="SQL dialect (postgres, mysql, sqlite, ansi)"),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
) -> None:
    """Diff two SQL schema files."""
    try:
        old_schema = parse_schema(str(old_file), dialect.lower())
        new_schema = parse_schema(str(new_file), dialect.lower())
        diff_result = diff_schemas(old_schema, new_schema)
        render_diff(diff_result, fmt, console)
    except FileNotFoundError as e:
        console.print(f"[red]File not found: {e.filename}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red bold]Error: {str(e)}[/red bold]")
        console.print("[dim]Check dialect, file format, or SQL validity.[/dim]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
