import json
import sys
from pathlib import Path
from typing import Dict, Any

import typer
from rich.console import Console
from rich.table import Table

from .simulator import CacheSimulator
from .trace_loader import load_trace
from .policies import LRUCache, LFUCache, FIFOCache, RandomCache

app = typer.Typer()
console = Console()

POLICY_MAP: Dict[str, type] = {
    "lru": LRUCache,
    "lfu": LFUCache,
    "fifo": FIFOCache,
    "random": RandomCache,
}

@app.command()
def main(
    trace_file: Path = typer.Argument(..., exists=True, help="Path to JSONL or CSV trace file"),
    cache_size: int = typer.Option(1_048_576, "--cache-size", "-s", help="Cache capacity in bytes (default: 1MB)"),
    policies: list[str] = typer.Option(["lru", "lfu", "fifo", "random"], "--policy", "-p"),
    output: Path = typer.Option(None, "--output", "-o", write=True, help="Export results to JSON"),
):
    """Simulate cache policies on access traces."""

    unknown = set(policies) - set(POLICY_MAP.keys())
    if unknown:
        typer.echo(f"Error: Unknown policies {list(unknown)}. Available: {list(POLICY_MAP)}", err=True)
        raise typer.Exit(1)

    # Load trace
    console.print(f"[info]Loading trace: {trace_file}")
    accesses = list(load_trace(trace_file))
    if not accesses:
        typer.echo("Error: Empty or invalid trace file.", err=True)
        raise typer.Exit(1)

    total_bytes = sum(size for _, size in accesses)
    console.print(f"[success]Loaded {len(accesses):,} accesses ({total_bytes / 1024 / 1024:.1f} MiB total)")

    # Run simulations
    results: Dict[str, Dict[str, Any]] = {}
    for pol_name in policies:
        console.print(f"\n[bold blue]Running {pol_name}[/bold blue]...")
        policy_cls = POLICY_MAP[pol_name]
        sim = CacheSimulator(policy_cls, cache_size)
        stats = sim.simulate(accesses)
        results[pol_name] = stats

    # Visualize
    table = Table(title="Cache Eviction Simulation Results")
    table.add_column("Policy", style="cyan")
    table.add_column("Hit Rate", justify="right")
    table.add_column("Byte Hit Rate", justify="right")
    table.add_column("Evictions", justify="right")
    table.add_column("Max Size (B)", justify="right")

    best_hit = max(results[p]["hit_rate"] for p in results)
    for pol, stats in results.items():
        hit_style = "bold green" if stats["hit_rate"] == best_hit else ""
        table.add_row(
            pol,
            f"{stats['hit_rate']:.1%}",
            f"{stats['byte_hit_rate']:.1%}",
            f"{stats['evictions']:,}",
            f"{stats['max_size']:,}",
            style=hit_style,
        )

    console.print(table)

    # Recommendation
    best_pol = max(results, key=lambda p: results[p]["hit_rate"])
    console.print(f"\n[bold green]Recommendation: {best_pol} (hit rate: {results[best_pol]['hit_rate']:.1%})[/bold green]")

    # Export
    if output:
        with output.open("w") as f:
            json.dump(results, f, indent=2, default=float)
        console.print(f"[green]Exported to {output}")

if __name__ == "__main__":
    app()