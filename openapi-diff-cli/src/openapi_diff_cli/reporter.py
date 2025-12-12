from typing import Dict, Any, List

from rich.box import ROUNDED

from rich.console import Console
from rich.table import Table

console = Console()

def print_table_report(result: Dict[str, Any]) -> None:
    summary = result["summary"]
    console.print(
        f"[bold cyan]Summary:[/bold cyan] "
        f"[bold red]{summary['breaking']}[/bold red] "
        f"breaking, "
        f"[bold green]{summary['non_breaking']}[/bold green] "
        f"non-breaking changes"
    )

    changes: List[Dict[str, Any]] = result["changes"]
    if not changes:
        console.print("[bold green]✅ No changes detected![/bold green]")
        return

    # Sort: breaking first, then by location
    sorted_changes = sorted(
        changes, key=lambda c: (c["impact"] != "breaking", c["location"])
    )

    table = Table(title="OpenAPI Changes", box=ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Type", style="white")
    table.add_column("Impact", style="bold")
    table.add_column("Description", style="italic")
    table.add_column("Old", no_wrap=False)
    table.add_column("New", no_wrap=False)

    for change in sorted_changes:
        impact = change["impact"]
        impact_style = "bold red" if impact == "breaking" else "bold green"
        old_str = (
            str(change["old_value"])[:60] + "..."
            if change["old_value"] is not None and len(str(change["old_value"])) > 60
            else str(change["old_value"])
        ) or "N/A"
        new_str = (
            str(change["new_value"])[:60] + "..."
            if change["new_value"] is not None and len(str(change["new_value"])) > 60
            else str(change["new_value"])
        ) or "N/A"
        table.add_row(
            change["location"],
            change["change_type"],
            f"[{impact_style}]{impact}[/{impact_style}]",
            change["description"],
            old_str,
            new_str,
        )

    console.print(table)
