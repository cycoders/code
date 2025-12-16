import json
from typing import NamedTuple

from rich.console import Console, Theme
from rich.table import Table
from rich import box
from rich.text import Text

from .differ import DiffResult
from .schema import Table


custom_theme = Theme({
    "added": "green",
    "removed": "red",
    "changed": "yellow",
    "info": "cyan",
})


EMOJIS = {"added": "🟢", "removed": "🔴", "changed": "🟡"}


def render_diff(diff: DiffResult, fmt: str, console: Console) -> None:
    """Render diff result to console or JSON."""
    if fmt == "json":
        from dataclasses import asdict
        console.print_json(data=diff._asdict())
        return

    total_changes = (
        len(diff.added_tables)
        + len(diff.removed_tables)
        + len(diff.changed_tables)
    )
    if total_changes == 0:
        console.print("[green bold]✅ No schema differences found.[/green bold]")
        return

    # Added tables
    if diff.added_tables:
        console.print(f"\n[added bold]{EMOJIS['added']} Added Tables ({len(diff.added_tables)}):[/added bold]")
        for name, table in diff.added_tables.items():
            console.print(f"  [added]{name}[/added] ({len(table.columns)} cols, {len(table.indexes)} indexes)")

    # Removed tables
    if diff.removed_tables:
        console.print(f"\n[removed bold]{EMOJIS['removed']} Removed Tables ({len(diff.removed_tables)}):[/removed bold]")
        for name in diff.removed_tables:
            console.print(f"  [removed]{name}[/removed]")

    # Changed tables
    if diff.changed_tables:
        console.print("\n[changed bold]{EMOJIS[\'changed']} Changed Tables ({len(diff.changed_tables)}):[/changed bold]")
        for table_name, changes in diff.changed_tables.items():
            console.print(f"  [changed bold]{table_name}:[/changed bold]")
            _render_table_changes(changes, console)


def _render_table_changes(changes: dict, console: Console) -> None:
    if "added_columns" in changes and changes["added_columns"]:
        console.print(f"    [added]+ Columns: {', '.join(changes['added_columns'])}[/added]")
    if "removed_columns" in changes and changes["removed_columns"]:
        console.print(f"    [removed]- Columns: {', '.join(changes['removed_columns'])}[/removed]")
    if "changed_columns" in changes and changes["changed_columns"]:
        console.print("    [changed]~ Column changes:[/changed]")
        for col, vals in changes["changed_columns"].items():
            old_desc = f"{vals['old'].type_} null={vals['old'].nullable} pk={vals['old'].primary_key}"
            new_desc = f"{vals['new'].type_} null={vals['new'].nullable} pk={vals['new'].primary_key}"
            console.print(f"      [changed]{col}: {old_desc} → {new_desc}[/changed]")
    if "added_indexes" in changes and changes["added_indexes"]:
        console.print(f"    [added]+ Indexes: {', '.join(changes['added_indexes'])}[/added]")
    if "removed_indexes" in changes and changes["removed_indexes"]:
        console.print(f"    [removed]- Indexes: {', '.join(changes['removed_indexes'])}[/removed]")
