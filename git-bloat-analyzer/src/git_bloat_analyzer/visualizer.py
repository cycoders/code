import json
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import git_bloat_analyzer.types as types
from git_bloat_analyzer.types import BlobInfo, PackInfo, RepoStats

console = Console()


def print_report(stats: RepoStats, blobs: List[BlobInfo], packs: List[PackInfo]):
    """Render beautiful report."""
    # Repo stats
    bloat_pct = f"{stats.bloat_score:.1f}%"
    console.print(
        Panel(
            f"[bold]Disk usage[/]: {stats.disk_usage_str} | "
            f"Packed: {stats.count_objects.get('size-pack', 'N/A')} | "
            f"Objects: {stats.count_objects.get('in-pack', 'N/A')} | "
            f"Bloat: [red]{bloat_pct}[/]",
            title="[bold blue]Repo Stats[/]",
        )
    )

    # Large blobs table
    if blobs:
        table = Table(title="Top Large Blobs")
        table.add_column("Path", style="cyan")
        table.add_column("Size", style="magenta")
        table.add_column("SHA (short)")
        for blob in blobs[:10]:  # Top 10
            table.add_row(blob.path or "N/A", blob.size_str, blob.sha)
        console.print(table)

    # Packs table
    if packs:
        table = Table(title="Top Packs")
        table.add_column("Packfile", style="green")
        table.add_column("Size")
        table.add_column("Objects")
        table.add_column("Comp Ratio", justify="right")
        for pack in packs[:5]:
            ratio_str = f"{pack.compression_ratio:.0f}%"
            table.add_row(pack.pack_file, pack.pack_size_str, str(pack.obj_count), ratio_str)
        console.print(table)

    # Fixes
    console.print("\n[bold green]Recommended Fixes[/bold green]")
    console.print("$ git reflog expire --expire=now --all")
    console.print("$ git prune-packed")
    console.print("$ git repack -a -d --depth=50 --window=50")
    console.print("$ git gc --aggressive --prune=now")
    if blobs:
        console.print(f"$ git filter-repo --path {blobs[0].path} --invert-paths --force  # Largest first")


def export_json(stats: RepoStats, blobs: List[BlobInfo], packs: List[PackInfo], output_path: Path):
    """Export structured JSON."""
    data = {
        "stats": stats.to_dict(),
        "large_blobs": [b.to_dict() for b in blobs],
        "packs": [p.to_dict() for p in packs],
    }
    output_path.write_text(json.dumps(data, indent=2))
    console.print(f"[green]Exported to {output_path}[/]")