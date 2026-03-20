from typing import List, Dict, Any
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


def render_results(results: List[Dict[str, Any]], fmt: str, console: Console):
    if fmt == "json":
        print(json.dumps(results, indent=2))
        return
    if fmt == "text":
        _render_text(results)
        return
    # rich default
    for res in results:
        name = res["name"]
        changes = res["changes"]
        table = Table(title=name, show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="green")
        if changes["added"]:
            table.add_row("Added", ", ".join(changes["added"]))
        if changes["removed"]:
            table.add_row("Removed", ", ".join(changes["removed"]), style="red")
        for k, v in changes["modified"].items():
            table.add_row(f"Modified {k}", str(v))
        console.print(table)
        compat_status = (
            Panel("✅ Backward & Forward compatible", style="green")
            if changes["backward_compatible"] and changes["forward_compatible"]
            else Panel("❌ Breaking changes detected", style="red")
        )
        console.print(compat_status)
        console.print()


def _render_text(results: List[Dict[str, Any]]):
    for res in results:
        print(f"Schema: {res['name']}")
        ch = res['changes']
        if ch['added']:
            print(f"  Added: {', '.join(ch['added'])}")
        if ch['removed']:
            print(f"  Removed: {', '.join(ch['removed'])}")
        for k, v in ch['modified'].items():
            print(f"  Modified {k}: {v}")
        bc = "Yes" if ch['backward_compatible'] else "No"
        fc = "Yes" if ch['forward_compatible'] else "No"
        print(f"  Backward compat: {bc}, Forward: {fc}\n")
