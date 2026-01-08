import sys
from typing import NamedTuple, Sequence, Tuple

import rich.console
import rich.table
from rich import box

from .models import ApiElement


class DiffResult(NamedTuple):
    removed: Sequence[ApiElement]
    changed: Sequence[Tuple[ApiElement, ApiElement]]
    added: Sequence[ApiElement]


def report(console: rich.console.Console, result: DiffResult, verbose: bool = False):
    """Print rich diff report. Exit 1 if breaking."""
    breaking = len(result.removed) + len(result.changed)

    if breaking == 0:
        console.print("[green]✅ No breaking changes detected.[/]\n")
        return

    console.print(f"[bold red]🚨 {breaking} BREAKING CHANGE{'S' if breaking > 1 else ''}:[/]\n")

    if result.removed:
        _render_table(console, "Removed", result.removed, "red")

    if result.changed:
        _render_changes(console, result.changed)

    if result.added or verbose:
        console.print("[green]➕ Added:[/]\n")
        _render_table(console, "Added", result.added, "green")

    sys.exit(1)


def _render_table(console, title: str, elements: Sequence[ApiElement], color: str):
    table = rich.table.Table(box=box.ROUNDED, title=f"[bold {color}]{title}[/]")
    table.add_column("Qualname", style="cyan")
    table.add_column("Kind", style="magenta")
    table.add_column("Args", max_width=40)
    for el in elements:
        args_str = ", ".join(f"{s.name}{'=*' if s.has_default else ''}" for s in el.arg_sigs) or "()"
        table.add_row(el.qualname, el.kind, args_str)
    console.print(table)
    console.print()


def _render_changes(console, changes: Sequence[Tuple[ApiElement, ApiElement]]):
    table = rich.table.Table(box=box.ROUNDED, title="[bold yellow]Changed[/]")
    table.add_column("Qualname", style="cyan")
    table.add_column("Kind", style="magenta")
    table.add_column("Old Args", max_width=30)
    table.add_column("New Args", max_width=30)
    for old, new in changes:
        old_args = ", ".join(f"{s.name}{'=*' if s.has_default else ''}" for s in old.arg_sigs) or "()"
        new_args = ", ".join(f"{s.name}{'=*' if s.has_default else ''}" for s in new.arg_sigs) or "()"
        table.add_row(old.qualname, old.kind, old_args, new_args)
    console.print(table)
    console.print()