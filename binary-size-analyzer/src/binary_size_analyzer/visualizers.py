import json
from typing import Dict, Any, List

import rich

import rich.table
import rich.tree
import rich.panel
from rich.console import Console
from rich.text import Text

from binary_size_analyzer.analyzer import SectionData, SymbolData, LibData


console = Console()


def human_size(size: int) -> str:
    """Format bytes to KiB/MiB."""
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.0f} GiB"


def spark_pct(pct: float) -> str:
    """Mini sparkline for %."""
    bars = " ▁▂▃▄▅▆▇█"
    idx = min(int(pct / 100 * len(bars)), len(bars) - 1)
    return bars[idx]


def print_overall_panel(data: Dict[str, Any], metric: str):
    overall = data["overall"]
    disk_str = human_size(overall["total_disk_bytes"])
    mem_str = human_size(overall["total_mem_bytes"])
    title = Text(f"{overall['format']} {overall['architecture']} ", style="bold white")
    title.append(f"Disk: {disk_str} | ")
    title.append(f"Mem: {mem_str}", style="cyan")

    summary = rich.table.Table.grid(expand=True)
    summary.add_column(justify="right")
    summary.add_column()
    summary.add_row("Sections", str(overall["sections_count"]))
    if overall["libs_count"]:
        summary.add_row("Libraries", str(overall["libs_count"]))

    panel = rich.panel.Panel(
        rich.panel.Panel(summary), title=title, border_style="bright_blue"
    )
    console.print(panel)


def print_sections_table(
    sections: List[Dict], metric: str, top_k: int
) -> None:
    data = sections[:top_k]
    table = rich.table.Table(title="Sections (Disk % desc)")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Disk", justify="right")
    table.add_column("Disk %", justify="right")
    if metric in ("mem", "both"):
        table.add_column("Mem", justify="right")
        table.add_column("Mem %", justify="right")
    table.add_column("Syms", justify="right")

    for s in data:
        disk_pct_spark = spark_pct(s["disk_pct"])
        row = [
            s["name"],
            human_size(s["disk_size"]),
            f"{s['disk_pct']:.1f}%{disk_pct_spark}",
        ]
        if metric in ("mem", "both"):
            mem_pct_spark = spark_pct(s["mem_pct"])
            row += [
                human_size(s["mem_size"]),
                f"{s['mem_pct']:.1f}%{mem_pct_spark}",
            ]
        row.append(str(s["symbols_count"]))
        table.add_row(*row)

    console.print(table)


def print_symbols_table(symbols: List[Dict], metric: str, top_k: int) -> None:
    data = symbols[:top_k]
    table = rich.table.Table(title="Top Symbols/Functions (Mem % desc)")
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Section", style="dim")
    table.add_column("Size", justify="right")
    table.add_column("%", justify="right")

    for sym in data:
        pct_spark = spark_pct(sym["pct"])
        table.add_row(sym["name"], sym["section"], human_size(sym["size"]), f"{sym['pct']:.2f}%{pct_spark}")
    console.print(table)


def print_libs_table(libs: List[Dict], top_k: int) -> None:
    table = rich.table.Table(title="Dynamic Libraries")
    table.add_column("Library")
    for lib in libs[:top_k]:
        table.add_row(lib["name"])
    console.print(table)


def print_tree_view(data: Dict[str, Any], metric: str, top_k: int) -> None:
    sections = data["sections"]
    symbols = data["symbols"]

    tree = rich.tree.Tree("Binary", style="bold cyan", guide_style="bright_blue")

    sections_node = tree.add("📁 Sections")
    for sec in sections[:12]:  # Limit tree depth
        style = "bold green" if sec["disk_pct"] > 20 else ""
        sec_node = sections_node.add(
            f"[blue]{sec['name']}[/]: {spark_pct(sec['disk_pct'])} {sec['disk_pct']:.1f}% disk / {sec['mem_pct']:.1f}% mem"
        )

        # Top symbols in this section
        sec_syms = [
            s for s in symbols if s["section"] == sec["name"]
        ][:5]
        sec_syms.sort(key=lambda x: x["size"], reverse=True)
        for sym in sec_syms:
            pct = sym["pct"]
            sym_node = sec_node.add(
                f"  💎 {sym['name'][:40]}... : {spark_pct(pct)} {pct:.2f}% ({human_size(sym['size'])} )"
            )

    console.print(tree)