from rich.table import Table
from rich import box
from typing import List, Dict, Any
from rich.markup import render

from terraform_plan_analyzer.parser import get_action


def build_change_table(changes: List[Dict[str, Any]]) -> Table:
    """Build Rich table for resource changes."""
    table = Table(
        title="Resource Changes",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Type", style="green")
    table.add_column("Action", style="bold")
    table.add_column("Key Changes", max_width=40)

    for change in changes:
        address = change["address"]
        rtype = change["type"]
        action = get_action(change)

        # Color by action
        action_style = "green" if action == "create" else "yellow" if "update" in action else "red"
        action_display = f"[{action_style}]{action.upper()}[/{action_style}]"

        # Diff keys
        before = change["change"].get("before", {})
        after = change["change"].get("after", {})
        changed_keys = set(after.keys()) - set(before.keys())
        if not changed_keys:
            changed_keys = {"metadata"}
        changes_str = ", ".join(sorted(changed_keys))[:37] + "..." if len(changed_keys) > 3 else ", ".join(changed_keys)

        table.add_row(address, rtype, action_display, changes_str)

    return table
