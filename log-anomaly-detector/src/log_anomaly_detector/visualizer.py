from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED

import pandas as pd


def display_anomalies(df: pd.DataFrame, console: Console) -> None:
    """Display anomalies in Rich table."""
    if df.empty:
        console.print("[green]✅ No anomalies detected.[/green]")
        return

    table = Table(title="🔍 Detected Anomalies", box=ROUNDED, show_header=True, header_style="bold magenta")

    # Common columns + anomaly flag
    common_cols = ["timestamp", "level", "duration_ms", "user_id", "endpoint"]
    display_cols = [c for c in common_cols if c in df.columns] + ["is_anomaly"]

    for col in display_cols:
        table.add_column(col.title(), no_wrap=col == "is_anomaly")

    for _, row in df.head(25).iterrows():
        cells = []
        for col in display_cols:
            val = row.get(col, "")
            if col == "is_anomaly" and val:
                cells.append("[red bold]●[/red bold]")
            else:
                cells.append(str(val))
        table.add_row(*cells)

    console.print(table)
    console.print(f"\n[bold cyan]📈 Total: {len(df)} anomalies[/bold cyan]")
    if len(df) > 25:
        console.print("[dim]... (showing top 25)[/dim]")
