import json
import logging
import sys
from pathlib import Path
from typing import List

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .analyzer import analyze_css_file, load_html_files, purge_used_css

app = typer.Typer()
console = Console()

@app.command()
def scan(
    html: List[Path] = typer.Argument(
        ..., help="HTML files or directories to scan recursively"
    ),
    css: List[Path] = typer.Argument(
        ..., help="CSS files or directories to analyze recursively"
    ),
    purge: bool = typer.Option(
        False, "--purge", "-p", help="Purge: generate _purged.css with used rules only (flattened)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="JSON stats instead of table"
    ),
):
    """
    Scan HTML/CSS for unused rules and report/purge.
    """
    logging.basicConfig(level=logging.WARNING)

    html_files = load_html_files(html)
    if not html_files:
        raise typer.BadParameter("No HTML files found. Provide --help for usage.")

    css_files = load_css_files(css)
    if not css_files:
        raise typer.BadParameter("No CSS files found.")

    stats = []
    for css_path in css_files:
        try:
            results = analyze_css_file(str(css_path), html_files)
            total_rules = len(results)
            total_size = sum(r["size"] for r in results)
            unused_rules = [r for r in results if not r["used"]]
            unused_size = sum(r["size"] for r in unused_rules)
            percent_unused = (unused_size / total_size * 100) if total_size > 0 else 0

            stat = {
                "css_file": str(css_path),
                "total_rules": total_rules,
                "unused_rules": len(unused_rules),
                "total_bytes": total_size,
                "unused_bytes": unused_size,
                "percent_unused": round(percent_unused, 1),
                "unused_selectors": [r["selector"] for r in unused_rules],
            }
            stats.append(stat)

            if not json_output:
                css_stem = css_path.stem
                rprint(
                    f"[bold cyan]CSS:[/bold cyan] {css_path.name}  "
                    f"[bold yellow]Unused:[/bold yellow] {percent_unused:.1f}% "
                    f"({unused_size}/{total_size} B)"
                )
                if unused_rules:
                    table = Table(title=f"Unused Rules in {css_stem}", show_header=True, header_style="bold magenta")
                    table.add_column("Selector", style="cyan")
                    table.add_column("Size", justify="right", style="green")
                    for r in unused_rules:
                        table.add_row(r["selector"], f"{r['size']} B")
                    console.print(table)
                else:
                    rprint("[green]All rules used![/green]")

                if purge:
                    purged_path = css_path.with_stem(css_path.stem + "_purged")
                    purge_used_css(results, purged_path)
                    rprint(f"[green]Purged → {purged_path}[/green]")

        except Exception as e:
            rprint(f"[red]Error analyzing {css_path}: {e}[/red]")
            continue

    if json_output:
        json.dump(stats, sys.stdout, indent=2)
        rprint()


def load_css_files(css_paths: List[Path]) -> List[Path]:
    css_files = []
    for p in css_paths:
        if p.is_file():
            if p.suffix.lower() == ".css":
                css_files.append(p)
        elif p.is_dir():
            css_files.extend(p.rglob("*.css"))
    return css_files

if __name__ == "__main__":
    app()