import math
from pathlib import Path
from typing import Optional

import rich.tree
import rich.table
import rich.panel
import rich.layout
from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .models import Stream, BlockingChain

console = Console()


def render_tree(streams: list[Stream], graph) -> None:
    tree = rich.tree.Tree("🌐 HTTP/2 Priority Tree", guide_style="cyan")
    levels = graph.compute_levels()

    def add_node(parent: rich.tree.Tree, sid: int, visited: set) -> None:
        if sid in visited:
            return
        visited.add(sid)
        s = streams[sid - 1]  # 1-indexed ids?
        label = Text(f"{s.name[:50]} (ID:{sid}, W:{s.priority.weight}) [{s.duration:.0f}ms]")
        if levels.get(sid, 0) > 2:
            label.stylize("red")
        node = parent.add(label)
        for child in graph.adj[sid]:
            add_node(node, child, visited)

    for sid in sorted(graph.streams, key=lambda s: levels.get(s, 0)):
        if streams[sid-1].priority.dependency == 0:
            add_node(tree, sid, set())

    console.print(tree)


def render_waterfall(streams: list[Stream], graph, output: Optional[Path] = None) -> None:
    if output:
        fig, ax = plt.subplots(figsize=(12, 8))
    else:
        console.print("\n🌊 Priority Waterfall (ms scale)")
        table = rich.table.Table(show_header=True, header_style="bold magenta")
        table.add_column("Stream", style="cyan")
        table.add_column("Start", justify="right")
        table.add_column("Dur", justify="right")
        table.add_column("Level", justify="right")
        table.add_column("Blocks", justify="right")

    levels = graph.compute_levels()
    max_dur = max((s.duration or 0 for s in streams), default=1)
    scale = 80 / max_dur  # ascii width

    for s in sorted(streams, key=lambda x: x.start_time or 0):
        start = (s.start_time or 0) / 1000
        dur = s.duration or 0
        lvl = levels.get(s.id, 0)
        color = "green" if lvl < 2 else "yellow" if lvl < 4 else "red"
        bar = "█" * int(dur * scale)
        console.print(f"[{color}]{s.name[:30]:30} [{start:5.0f}-{start+dur:5.0f}] {bar} L{lvl}")

        if output and output.suffix == ".svg":
            ax.add_patch(Rectangle((start, s.id), dur, 0.8, fc=color, ec="black"))
            ax.text(start + dur/2, s.id + 0.4, s.name[:20], ha="center", va="center", fontsize=8)

    if output:
        ax.set_ylim(0, len(streams) + 1)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Streams")
        plt.savefig(output)
        console.print(f"💾 Waterfall saved: {output}")


def render_suggestions(graph) -> None:
    suggs = graph.suggestions()
    if suggs:
        panel = rich.panel.Panel.fit("💡 Optimization Suggestions", title="Perf Wins")
        for s in suggs:
            console.print(f"• {s}")
    else:
        console.print("✅ Priorities look optimal!")


def render_chains(chains: list[BlockingChain]) -> None:
    if chains:
        console.print("\n🔗 Top Blocking Chains:")
        for i, chain in enumerate(chains[:3], 1):
            names = [str(stream.id) for stream in chain.streams]
            console.print(f"  {i}. {' → '.join(names)} ({chain.total_block_ms:.0f}ms block)")
