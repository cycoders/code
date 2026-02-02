import json
import sys
import typer
from pathlib import Path
from typing import Optional

from rich import console

from .analyzer import analyze_binary


console = console.Console()

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command(help="Inspect binary size breakdown")
def inspect(
    path: Path = typer.Argument(..., exists=True, help="Path to ELF/PE/Mach-O binary"),
    metric: str = typer.Option(
        "both", "--metric", help="disk, mem, or both (default)"),
    view: str = typer.Option(
        "sections",
        "--view",
        help="sections (default), symbols, libs",
    ),
    fmt: str = typer.Option("table", "--format", help="table (default), tree, json"),
    top_k: int = typer.Option(20, "--top", min=1, max=100, help="Top N items"),
):
    """
    Visualize binary bloat: sections, symbols, libs with % disk/mem usage.

    Examples::

        $ python -m binary_size_analyzer inspect ./myapp --view symbols --metric mem
        $ python -m binary_size_analyzer inspect /bin/ls --format json | jq
    """
    try:
        data = analyze_binary(str(path))

        if fmt == "json":
            typer.echo(json.dumps(data, indent=2))
            raise typer.Exit(0)

        from .visualizers import (
            print_overall_panel,
            print_sections_table,
            print_symbols_table,
            print_libs_table,
            print_tree_view,
        )

        print_overall_panel(data, metric)
        print_sections_table(data["sections"], metric, top_k)

        if view == "symbols":
            print_symbols_table(data["symbols"], metric, top_k)
        elif view == "libs":
            print_libs_table(data["libs"], top_k)
        elif view == "tree":
            print_tree_view(data, metric, top_k)
        else:
            console.print("[yellow]Use --view=tree for hierarchical drill-down[/yellow]")

    except FileNotFoundError:
        typer.echo("[red]Error:[/red] Binary not found", err=True)
        raise typer.Exit(1)
    except Exception as e:
        console.print_exception(show_locals=False)
        typer.echo(f"[red]Failed to analyze {path}: {e}[/red]", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()