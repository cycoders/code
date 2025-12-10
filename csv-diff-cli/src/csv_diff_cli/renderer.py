from typing import Any, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import json


def render_diff(result: Dict[str, Any], fmt: str = "table") -> None:
    """
    Render diff result to stdout in table or JSON format.
    """
    if fmt == "json":
        print(json.dumps(result, default=str, indent=2))
        return

    console = Console()

    # Header
    console.print(Panel("[bold cyan]CSV Diff Report[/bold cyan]", expand=False))

    # Stats
    stats = result["stats"]
    stats_table = Table("Metric", "Left", "Right", title="Stats", box=Table.Box.ROUNDED)
    stats_table.add_row("Rows", str(stats["rows_left"]), str(stats["rows_right"]))
    stats_table.add_row("Matches", str(stats["matches"]), str(stats["matches"]))
    stats_table.add_row("Only Left", str(stats["only_left"]), "")
    stats_table.add_row("Only Right", "", str(stats["only_right"]))
    console.print(stats_table)

    schema_diff = result["schema_diff"]
    if schema_diff["only_in_1"]:
        console.print(f"[red]Columns only in left: {', '.join(schema_diff['only_in_1'])}[/red]")
    if schema_diff["only_in_2"]:
        console.print(f"[green]Columns only in right: {', '.join(schema_diff['only_in_2'])}[/green]")

    if schema_diff["dtype_mismatches"]:
        dt_table = Table("Column", "Left Type", "Right Type", box=Table.Box.ROUNDED)
        for col, (left, right) in schema_diff["dtype_mismatches"].items():
            dt_table.add_row(col, left, right)
        console.print(dt_table)

    # Removed rows
    only_left_count = stats["only_left"]
    if only_left_count > 0:
        console.print(f"[yellow]Removed rows: {only_left_count}[/yellow]")
        removed = result["removed_rows"]
        if len(removed) <= 20:
            console.print(Table.from_df(removed, box=Table.Box.ROUNDED))
        else:
            console.print(Table.from_df(removed.head(20), box=Table.Box.ROUNDED))
            console.print("... (truncated)")

    # Added rows
    only_right_count = stats["only_right"]
    if only_right_count > 0:
        console.print(f"[green]Added rows: {only_right_count}[/green]")
        added = result["added_rows"]
        if len(added) <= 20:
            console.print(Table.from_df(added, box=Table.Box.ROUNDED))
        else:
            console.print(Table.from_df(added.head(20), box=Table.Box.ROUNDED))
            console.print("... (truncated)")

    # Cell changes
    changes = result["cell_changes"]
    if changes:
        console.print(f"[orange1]Cell changes: {len(changes)}[/orange1]")
        change_table = Table(
            "Row (Left)", "Key", "Column", "Old Value", "New Value",
            box=Table.Box.ROUNDED, title="Changes"
        )
        for change in sorted(changes, key=lambda c: (c.get("row_idx_left", 0), c["col"])):
            change_table.add_row(
                str(change.get("row_idx_left", "N/A")),
                str(change["key"]),
                change["col"],
                str(change["old"]),
                str(change["new"]),
            )
        console.print(change_table)
    else:
        console.print("[bold green]✓ No cell differences![/bold green]")

    if not any([schema_diff["only_in_1"], schema_diff["only_in_2"], schema_diff["dtype_mismatches"], only_left_count, only_right_count, changes]):
        console.print("[bold green]✓ Files are identical![/bold green]")