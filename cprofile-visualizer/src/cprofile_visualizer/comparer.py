from pathlib import Path
from rich.console import Console
from rich.table import Table
import pstats
from typing import Tuple, List
from .parser import get_sort_key

DeltaRow = Tuple[str, float, float, float, float]


def render_compare(
    stats1: pstats.Stats,
    stats2: pstats.Stats,
    limit: int,
    console: Console,
    sort_by: str,
) -> None:
    """Render delta table: cumtime1, cumtime2, delta, %change."""

    all_keys: set[tuple] = set(stats1.stats.keys()) | set(stats2.stats.keys())
    deltas: List[DeltaRow] = []

    for key in all_keys:
        ct1_tuple = stats1.stats.get(key, (0, 0, 0, 0, 0))
        ct2_tuple = stats2.stats.get(key, (0, 0, 0, 0, 0))
        ct1: float = ct1_tuple[3]
        ct2: float = ct2_tuple[3]
        delta = ct2 - ct1
        pct_change = ((ct2 - ct1) / ct1 * 100) if ct1 > 0 else 0.0
        func = f"{key[2]} ({Path(key[0]).name}:{key[1]})"
        deltas.append((func, ct1, ct2, delta, pct_change))

    # Sort
    if sort_by == "pct":
        deltas.sort(key=lambda row: abs(row[4]), reverse=True)
    else:  # delta
        deltas.sort(key=lambda row: abs(row[3]), reverse=True)

    table = Table(
        title="⚖️  Profile Diff (file1 ← file2)",
        caption=f"Sorted by {sort_by} (red=regression, green=improvement)",
        box=None,
        show_header=True,
        header_style="bold yellow",
    )
    table.add_column("function", style="blue", ratio=2)
    table.add_column("cum1", justify="right")
    table.add_column("cum2", justify="right")
    table.add_column("delta", justify="right")
    table.add_column("%chg", justify="right")

    for func, ct1, ct2, delta, pct in deltas[:limit]:
        delta_color = "red" if delta > 0 else "green"
        pct_color = "red" if pct > 0 else "green"
        pct_str = f"{pct:+5.1f}%"
        delta_str = f"{delta:+7.3f}s"
        table.add_row(
            func,
            f"{ct1:6.3f}s",
            f"{ct2:6.3f}s",
            f"[{delta_color]" + delta_str + "[/]",
            f"[{pct_color]" + pct_str + "[/]",
        )

    console.print(table)
