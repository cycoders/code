import csv
import json
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table


def output_results(results: List[Dict[str, Any]], fmt: str, console: Console):
    """Output results in specified format."""
    opens = [r for r in results if r["open"]]
    if not opens:
        console.print("[yellow]No open ports found.[/]")
        return

    if fmt == "table":
        table = Table(title="Open Ports Summary", show_header=True, header_style="bold magenta")
        table.add_column("IP", style="cyan")
        table.add_column("Port", justify="right", style="green")
        table.add_column("Service", style="bold yellow")
        table.add_column("Banner Preview", style="dim")
        table.add_column("Duration", justify="right")

        for r in opens:
            banner_prev = (
                r["banner"][:50] + "..." if len(r["banner"]) > 50 else r["banner"]
            )
            table.add_row(
                r["ip"],
                str(r["port"]),
                r["service"],
                banner_prev,
                f"{r['duration']:.2f}s",
            )
        console.print(table)

    elif fmt == "json":
        # Filter opens only
        print(json.dumps(opens, default=str, indent=2))

    elif fmt == "csv":
        if opens:
            writer = csv.DictWriter(console.file, fieldnames=opens[0].keys())
            writer.writeheader()
            writer.writerows(opens)
        else:
            console.print("[yellow]No open ports for CSV.[/]")

    else:
        console.print(f"[red]Unknown output format: {fmt}[/]")