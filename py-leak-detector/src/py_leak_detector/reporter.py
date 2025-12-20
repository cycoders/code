from typing import Any
from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import typer
from .analyzer import RSSAnalysis, HeapAnalysis, HeapLeak


def print_report(console: Console, rss: RSSAnalysis, heap: HeapAnalysis) -> None:
    # RSS Panel
    lines = []
    for t, r, d in zip(rss.timestamps, rss.history_mb, [0] + rss.deltas_mb):
        delta_str = f"▲{d:.1f}MB" if d > 0 else ""
        lines.append(f"{t:5.0f}s {r:6.1f}MB {delta_str}")
    rss_panel = Panel("\n".join(lines[-10:]), title="[bold cyan]RSS Over Time (last 10)[/]")
    console.print(rss_panel)

    # RSS Stats
    if rss.is_leak:
        console.print(f"[bold red]🚨 RSS Leak![/] max Δ {rss.max_delta_mb:.1f}MB > {rss.max_delta_mb:.1f}MB thresh")
    console.print(f"Total growth: {rss.total_growth_mb:.1f}MB | Rate: {rss.avg_delta_mb_per_s:.2f} MB/s")

    # Heap
    if heap.is_leak and heap.leaks:
        table = Table(title="[bold orange3]Top Heap Leaks (>thresh)[/bold orange3]", box=box.ROUNDED)
        table.add_column("Size Δ", style="red")
        table.add_column("Count Δ")
        table.add_column("Location")
        for leak in heap.leaks[:10]:
            size_mb = leak.size_diff / (1024**2)
            table.add_row(f"{size_mb:.1f}MB", str(leak.count_diff), leak.location)
        console.print(table)
    else:
        console.print("[green]✅ No significant heap leaks.[/green]")


def report_session(console: Console, session_dir: Path) -> None:
    # Load
    import json
    rss_data = json.loads((session_dir / "rss_history.json").read_text())
    timestamps = rss_data["timestamps"]
    rss_mb = rss_data["rss_mb"]

    snaps = sorted(session_dir.glob("snapshot_*.pytrace"))
    snapshots = [tracemalloc.Snapshot.load(str(s)) for s in snaps]

    # Reuse analyzer/reporter
    from .analyzer import analyze_rss, analyze_heap_diffs
    rss_ana = analyze_rss(rss_mb, timestamps, 50.0)
    heap_ana = analyze_heap_diffs(snapshots, 1_048_576)
    print_report(console, rss_ana, heap_ana)
