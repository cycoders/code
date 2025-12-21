import json
import csv
from typing import Any
from rich.console import Console
from rich.table import Table
from rich import box

from .stats import OwnershipStats

console = Console()

def render_stats(stats: OwnershipStats, top: int = 10, fmt: str = "table") -> None:
    """Render stats in chosen format."""
    if fmt == "json":
        console.print_json(data=stats._asdict())
        return
    if fmt == "csv":
        writer = csv.DictWriter(console.file, fieldnames=["author", "pct"])
        writer.writeheader()
        for a, p in stats.top_authors[:top]:
            writer.writerow({"author": a, "pct": f"{p:.1f}"})
        return

    # Table: Authors
    table = Table(title="Code Ownership by Author", box=box.ROUNDED)
    table.add_column("Author", style="cyan")
    table.add_column("Lines", justify="right")
    table.add_column("%", justify="right")
    for author, pct in stats.top_authors[:top]:
        lines = int(stats.total_lines * (pct / 100))
        table.add_row(author, str(lines), f"{pct:.1f}%")
    console.print(table)

    # Ext table
    if stats.ext_ownership:
        ext_table = Table(title="Top Ownership by Filetype", box=box.ROUNDED)
        ext_table.add_column("Ext", style="magenta")
        ext_table.add_column("Top Owner", style="green")
        ext_table.add_column("% within ext")
        for ext, auth_counts in stats.ext_ownership.items():
            top_auth, top_count = auth_counts.most_common(1)[0]
            total_ext = sum(auth_counts.values())
            pct = top_count / total_ext * 100 if total_ext else 0
            ext_table.add_row(ext, top_auth, f"{pct:.0f}%")
        console.print(ext_table)

    console.print(f"\nTotal lines analyzed: {stats.total_lines:,}")
