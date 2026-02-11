import json
from pathlib import Path
from typing import Dict
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from .types import ImageDiff, LayerDelta

console = Console()


def format_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def format_delta(delta: int) -> str:
    sign = "+" if delta > 0 else ""
    return f"{sign}{format_size(abs(delta))}"


def render_diff(diff: ImageDiff, fmt: str = "table"):
    if fmt == "json":
        print(json.dumps(diff.to_dict(), indent=2))
        return

    # Summary table
    table = Table(box=box.ROUNDED, title=f"Container Diff: {diff.image1_name} → {diff.image2_name}")
    table.add_column("Aspect", style="cyan")
    table.add_column(diff.image1_name, justify="right")
    table.add_column(diff.image2_name, justify="right")
    table.add_column("Delta", justify="right")

    delta_color = "green" if diff.size_delta >= 0 else "red"
    table.add_row("Size", format_size(diff.size1), format_size(diff.size2), Text(format_delta(diff.size_delta), style=delta_color))
    table.add_row("Layers", str(diff.num_layers1), str(diff.num_layers2), str(diff.num_layers2 - diff.num_layers1))
    table.add_row("OS", diff.os1, diff.os2, "=" if diff.os1 == diff.os2 else "≠")
    table.add_row("Arch", diff.arch1, diff.arch2, "=" if diff.arch1 == diff.arch2 else "≠")

    console.print(table)

    # Layers table
    if diff.layer_deltas:
        ltable = Table(box=box.MINIMAL, title="RootFS Layers", show_header=True)
        ltable.add_column("SHA", style="dim")
        ltable.add_column("Status")
        ltable.add_column("Size 1", justify="right")
        ltable.add_column("Size 2", justify="right")
        ltable.add_column("Delta", justify="right")

        for ld in sorted(diff.layer_deltas, key=lambda l: l.size_delta or 0, reverse=True)[:20]:  # Top 20
            s1 = format_size(ld.size1) if ld.size1 else "-"
            s2 = format_size(ld.size2) if ld.size2 else "-"
            d = format_delta(ld.size_delta) if ld.size_delta is not None else "-"
            status_style = "green" if ld.status == "same" else "yellow" if ld.status == "changed" else "blue" if ld.status == "added" else "red"
            ltable.add_row(ld.sha, Text(ld.status.title(), style=status_style), s1, s2, d)

        console.print(ltable)

    # Config changes
    if diff.config_delta.changed_keys or diff.config_delta.added_keys or diff.config_delta.removed_keys:
        ctable = Table(box=box.MINIMAL, title="Config Changes")
        ctable.add_column("Key")
        ctable.add_column("Before")
        ctable.add_column("After")
        for k, (v1, v2) in sorted(diff.config_delta.changed_keys.items()):
            ctable.add_row(k, v1 or "-", v2 or "-")
        console.print(ctable)
