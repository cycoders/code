from typing import Optional

import rich.text
from rich.table import Table
from rich.console import Console
from rich.box import Box

from .models import LogSummary


def compare_summaries(
    s1: LogSummary, s2: LogSummary, console: Optional[Console] = None
) -> None:
    """Render side-by-side comparison with deltas."""
    console = console or Console()
    console.print(
        f"[bold cyan]Comparing:[/] [green]{s1.filename}[/] ← [yellow]{s2.filename}[/]"
    )

    step_map1 = {s.name.lower(): s for s in s1.steps}
    step_map2 = {s.name.lower(): s for s in s2.steps}
    all_steps = sorted(set(step_map1) | set(step_map2))

    comp_table = Table(title="Performance Comparison", box=Box.DOUBLE, expand=True)
    comp_table.add_column("Step", style="cyan", no_wrap=True)
    comp_table.add_column("Dur 1", justify="right")
    comp_table.add_column("Dur 2", justify="right")
    comp_table.add_column("Delta", justify="right")

    for step_name in all_steps[:25]:
        d1 = step_map1.get(step_name)
        d2 = step_map2.get(step_name)
        dur1 = d1.duration if d1 else 0
        dur2 = d2.duration if d2 else 0
        if dur1 > 0 and dur2 > 0:
            delta = dur2 - dur1
            pct = (delta / dur1) * 100
            delta_str = f"{delta:+.1f}s ({pct:+.0f}%)"
            style = "red" if delta > 0 else "green"
            comp_table.add_row(
                step_name[:30],
                f"{dur1:.1f}s",
                f"{dur2:.1f}s",
                rich.text.Text(delta_str, style=style),
            )

    console.print(comp_table)

    tot1 = s1.total_duration or 0
    tot2 = s2.total_duration or 0
    if tot1 > 0:
        delta_tot = tot2 - tot1
        pct_tot = (delta_tot / tot1) * 100
        style_tot = "red" if delta_tot > 0 else "green"
        console.print(
            rich.text.Text(
                f"\n[bold]Overall Delta: {delta_tot:+.1f}s ({pct_tot:+.0f}%)[/]",
                style=style_tot,
            )
        )

    console.print(f"[dim]Errors: {s1.total_errors} → {s2.total_errors} | Warnings: {s1.total_warnings} → {s2.total_warnings}[/]")