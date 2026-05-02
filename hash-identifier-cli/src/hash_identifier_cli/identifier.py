from typing import List

from rich.console import Console

from .hashes import HASHES_BY_HEX_LEN, HashInfo


console = Console()


def _normalize_hex(hex_str: str) -> str:
    hex_str = hex_str.strip().lower()
    if not all(c in "0123456789abcdef" for c in hex_str):
        raise ValueError("Input must be valid hexadecimal.")
    if len(hex_str) % 2 != 0:
        raise ValueError("Hex string must have even length.")
    return hex_str


def identify(hex_str: str, show_all: bool = False) -> List[HashInfo]:
    """
    Identify possible hash algorithms for given hex digest.

    Returns top candidates sorted by priority.
    """
    try:
        hex_str = _normalize_hex(hex_str)
        byte_len = len(hex_str) // 2
        candidates = HASHES_BY_HEX_LEN.get(byte_len, [])
        if not candidates:
            return []
        # Sort by priority descending
        candidates = sorted(candidates, key=lambda h: h["priority"], reverse=True)
        if show_all:
            return candidates[:20]  # Limit output
        return candidates[:5]
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return []


def format_results(results: List[HashInfo], hex_str: str = "") -> None:
    if not results:
        console.print("[yellow]No known hash algorithms match this digest.[/yellow]")
        return

    from rich.table import Table

    table = Table(title=f"Candidates for {hex_str[:16]}... (len={len(hex_str)} hex chars)")
    table.add_column("Algorithm", style="cyan")
    table.add_column("Priority", justify="right", style="green")
    table.add_column("Sample", style="dim")

    for h in results:
        sample = h["samples"][0][:16] + "..." if h["samples"] else "N/A"
        table.add_row(h["name"], str(h["priority"]), sample)

    console.print(table)


__all__ = ["identify", "format_results"]