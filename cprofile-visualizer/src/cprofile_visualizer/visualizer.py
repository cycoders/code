from typing import Any
from rich.console import Console, ConsoleRenderable
from rich.table import Table
from rich.tree import Tree
from rich import box
import pstats


def render_table(stats: pstats.Stats, limit: int, console: Console) -> None:
    """Render top N as rich table."""
    table = Table(
        title="🔥 Top Functions",
        caption="(ncalls | tottime | tpercall | cumtime | cpercall | func)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("ncalls", style="cyan", no_wrap=True)
    table.add_column("tottime", justify="right", style="green")
    table.add_column("t/per", justify="right", style="green")
    table.add_column("cumtime", justify="right", style="red")
    table.add_column("c/per", justify="right", style="red")
    table.add_column("function", style="blue", ratio=2)

    top_n = min(limit, len(stats.fcn_list))
    for i in range(top_n):
        key = stats.fcn_list[i]
        nc, tt, _, ct, _ = stats.stats[key]
        t_per = tt / nc if nc else 0.0
        c_per = ct / nc if nc else 0.0
        func = f"{key[2]} (in {Path(key[0]).name}:{key[1]})"
        table.add_row(
            f"{nc:,}",
            f"{tt:.3f}s",
            f"{t_per:.4f}s",
            f"{ct:.3f}s",
            f"{c_per:.4f}s",
            func,
        )
    console.print(table)


def render_tree(stats: pstats.Stats, limit: int, console: Console) -> None:
    """Render top calls as tree (flat for simplicity, with top callees)."""
    tree = Tree("🌳 Call Tree (Top by cumtime, depth=1)", guide_style="cyan")

    top_n = min(limit, len(stats.fcn_list))
    for i in range(top_n):
        key = stats.fcn_list[i]
        _, _, _, ct, _ = stats.stats[key]
        node_label = f"[bold cyan]{key[2]}[/bold cyan] [red]{ct:.3f}s[/] [dim]{Path(key[0]).name}:{key[1]}[/]"
        node = tree.add(node_label)

        # Add top 3 callees
        callees = stats.all_callees.get(key, {})
        sorted_callees = sorted(
            callees.keys(),
            key=lambda k: stats.stats.get(k, (0, 0, 0, 0, 0))[3],
            reverse=True,
        )[:3]
        for callee_key in sorted_callees:
            _, _, _, c_ct, _ = stats.stats[callee_key]
            node.add(f"  ↳ [dim]{callee_key[2]}[/]: {c_ct:.3f}s")

    console.print(tree)


def render_flame(stats: pstats.Stats, limit: int, console: Console) -> None:
    """ASCII flame bars (proportional to cumtime)."""
    if not stats.fcn_list:
        console.print("[yellow]No stats.[/]"))
        return

    total_time = stats.stats[stats.fcn_list[0]][3]  # Top cumtime ≈ total runtime
    console.print(f"[bold]🔥 Flame Graph (cumtime % of {total_time:.3f}s)[/]")

    BAR_WIDTH = 60
    top_n = min(limit, len(stats.fcn_list))
    for i in range(top_n):
        key = stats.fcn_list[i]
        nc, tt, _, ct, _ = stats.stats[key]
        pct = (ct / total_time) * 100 if total_time > 0 else 0
        bar_len = min(int((ct / total_time) * BAR_WIDTH), BAR_WIDTH)
        bar = "█" * bar_len + "░" * (BAR_WIDTH - bar_len)
        func_short = f"{key[2][:35]}..." if len(key[2]) > 35 else key[2]
        loc = f"{Path(key[0]).name}:{key[1]}"
        console.print(f"{func_short:<40} |[bold]{bar}[/bold]| {ct:.3f}s ({pct:5.1f}%) [dim]{loc}[/]")
