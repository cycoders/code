import sys
import typing as t
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from binary_diff_cli.differ import compare_paths, get_file_sizes
from binary_diff_cli.analyzer import compute_stats, entropy_bars
from binary_diff_cli.renderer import highlight_hex

app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)


@app.command()
def diff(
    file1: Path = typer.Argument(..., exists=True, metavar="FILE1"),
    file2: Path = typer.Argument(..., exists=True, metavar="FILE2"),
    lines: int = typer.Option(20, "--lines", "-l", min=1, show_default=True),
    block_size: int = typer.Option(16, "--block-size", "-b", min=1, max=64, show_default=True),
) -> None:
    """Compare two binary files with side-by-side hex view."""
    size1, size2 = get_file_sizes(file1, file2)
    if size1 != size2:
        console.print(f"[yellow]⚠️ Sizes differ:[/] {size1:,} vs {size2:,} bytes")

    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column("Offset", width=10, style="bold cyan", justify="right")
    table.add_column("File 1", width=48, style="bold green")
    table.add_column("ASCII1", width=16)
    table.add_column("File 2", width=48, style="bold magenta")
    table.add_column("ASCII2", width=16)
    table.add_column("#Chg", width=4, justify="right", style="bold yellow")

    row_count = 0
    for block in compare_paths(file1, file2, block_size):
        hl1 = highlight_hex(block["hex1"], block["diff_positions"])
        hl2 = highlight_hex(block["hex2"], block["diff_positions"])
        table.add_row(
            f"{block['offset']:08x}",
            hl1,
            block["ascii1"],
            hl2,
            block["ascii2"],
            str(block["changes"]),
        )
        row_count += 1
        if row_count >= lines:
            break

    console.print(table)
    if row_count >= lines:
        console.print("[dim]... more lines: rerun with --lines N[/]")


@app.command()
def analyze(
    file1: Path = typer.Argument(..., exists=True),
    file2: Path = typer.Argument(..., exists=True),
    sample_bytes: int = typer.Option(1024 * 1024, "--sample-bytes", show_default=False),
) -> None:
    """Compute detailed statistics and histograms."""
    stats = compute_stats(file1, file2, sample_bytes)

    table = Table(title="Binary Diff Stats", show_header=True, box="heavy")
    table.add_column("Metric", style="cyan")
    table.add_column("File 1", justify="right", style="green")
    table.add_column("File 2", justify="right", style="magenta")
    table.add_column("Delta", justify="right")

    table.add_row("Size", f"{stats['size1']:,}", f"{stats['size2']:,}", f"{stats['size_delta']:,}")
    table.add_row("Changed Bytes", "-", "-", f"{stats['changed']:,} ({stats['change_pct']:.1%})")
    table.add_row("Entropy", f"{stats['entropy1']:.2f}", f"{stats['entropy2']:.2f}", f"Δ{stats['entropy_delta']:+.2f}")

    console.print(table)

    # Top bytes
    console.print("\n[bold]Top 5 Bytes:[/] [green]File1[/] | [magenta]File2[/]")
    for byte1, byte2 in zip(stats["top1"], stats["top2"]):
        b1, c1, p1 = byte1
        b2, c2, p2 = byte2
        console.print(f"[green]{b1:02x}[/] ({c1:,} {p1:.1%}) | [magenta]{b2:02x}[/] ({c2:,} {p2:.1%})")


@app.command()
def plot(
    file_path: Path = typer.Argument(..., exists=True),
    kind: str = typer.Option("entropy", "--type", "-t", show_default=True),
) -> None:
    """Render ASCII heatmap (entropy or histogram)."""
    if kind == "entropy":
        plot_text = entropy_bars(file_path)
        console.print(Panel(plot_text, title=f"Entropy Heatmap: {file_path.name}", width=82, height=22))
    else:
        raise typer.BadParameter(f"Unknown plot type: {kind}")


if __name__ == "__main__":
    app()