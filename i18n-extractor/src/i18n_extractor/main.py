import logging
import sys
from pathlib import Path
from typing import List, Set

import typer
import rich.console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from collections import Counter, defaultdict

from .extractor import scan_paths
from .writer import write_po
from .types import Message

app = typer.Typer(no_args_is_help=True)
console = rich.console.Console()

@app.command()
def scan(
    paths: List[Path] = typer.Argument(..., help="Paths to scan"),
    function: List[str] = typer.Option(["_"], "--function/-f", help="Translation functions"),
    plural_function: List[str] = typer.Option(["ngettext"], "--plural-function/-p", help="Plural functions"),
    output: Optional[Path] = typer.Option(None, "--output/-o", help="Output PO file"),
    dry_run: bool = typer.Option(False, "--dry-run/-d"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    """Extract translatable strings from Python files."""
    if verbose:
        logging.basicConfig(level=logging.INFO)
    functions: Set[str] = set(function)
    plural_functions: Set[str] = set(plural_function)

    all_messages: List[Message] = []
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning...", total=None)
        for file_messages in scan_paths(paths, functions, plural_functions):
            all_messages.extend(file_messages)
            progress.advance(task)

    if not all_messages:
        console.print("[yellow]No translatable strings found.[/yellow]")
        raise typer.Exit(0)

    if dry_run:
        _show_stats(all_messages)
    elif output:
        write_po(all_messages, output)
        console.print(f"[green]Wrote {len(all_messages)} messages to {output}[/green]")
    else:
        typer.echo("Use --output or --dry-run", err=True)
        raise typer.Exit(1)


def _show_stats(messages: List[Message]) -> None:
    table = Table(title="Extracted Strings")
    table.add_column("Preview", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Locations")

    counter = Counter(msg.singular for msg in messages)
    locs = defaultdict(set)
    for msg in messages:
        locs[msg.singular].add(msg.location[1])

    for singular, count in counter.most_common(20):
        loc_str = "/".join(map(str, sorted(locs[singular])))[:30] + "..." if len(locs[singular]) > 2 else "/".join(map(str, sorted(locs[singular])))
        table.add_row(singular[:40] + "..." if len(singular) > 40 else singular, str(count), loc_str)

    console.print(table)

if __name__ == "__main__":
    app()