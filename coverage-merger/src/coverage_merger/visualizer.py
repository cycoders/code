from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import jinja2
from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich.text import Text
from rich import box

from .merger import parse_coverage_xml, compute_stats


console = Console()


def print_table(
    stats: List[Dict[str, Any]], prev_path: Optional[Path] = None
) -> None:
    """Print Rich table with coverage stats and optional deltas."""
    prev_stats: Dict[str, Dict[str, float]] = {}
    if prev_path and prev_path.exists():
        prev_data = parse_coverage_xml(prev_path)
        prev_s = compute_stats(prev_data)
        prev_stats = {s["file"]: s for s in prev_s}

    table = Table(
        title="[bold magenta]Coverage Summary[/]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Lines %", justify="right")
    table.add_column("Branch %", justify="right")
    table.add_column("Δ Lines", justify="right")
    table.add_column("Missed", justify="right")

    for stat in stats:
        file = stat["file"]
        line_pct = stat["line_pct"]
        branch_pct = stat["branch_pct"]

        # Line % color
        line_style = "green" if line_pct >= 90 else "yellow" if line_pct >= 80 else "red"
        line_text = Text(f"{line_pct:.1f}%", style=line_style)

        # Branch %
        branch_text = Text("-") if branch_pct is None else Text(
            f"{branch_pct:.1f}%",
            style="green" if branch_pct >= 90 else "yellow" if branch_pct >= 80 else "red",
        )

        # Delta
        delta_str = ""
        if prev_path:
            pstat = prev_stats.get(file)
            if pstat:
                delta = line_pct - pstat["line_pct"]
                delta_style = "green" if delta >= 0 else "red"
                delta_str = Text(f"{delta:+.1f}%", style=delta_style)
            else:
                delta_str = Text("+∞%", style="green")  # New file
        delta_text = delta_str or Text("-")

        # Missed
        missed_text = Text(str(stat["missed_lines"]), style="red" if stat["missed_lines"] > 0 else "green")

        table.add_row(file, line_text, branch_text, delta_text, missed_text)

    console.print(table)


def generate_html(
    merged_data: Dict[str, Any],
    html_path: Path,
    prev_path: Optional[Path] = None,
) -> None:
    """Generate HTML report using Jinja2."""
    stats = compute_stats(merged_data)
    prev_stats_dict = {}
    if prev_path and prev_path.exists():
        prev_data = parse_coverage_xml(prev_path)
        prev_s = compute_stats(prev_data)
        prev_stats_dict = {s["file"]: s["line_pct"] for s in prev_s}

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("src/coverage_merger/templates"))
    template = env.get_template("index.html.j2")
    html_content = template.render(
        stats=stats,
        prev_stats=prev_stats_dict,
        total_files=len(stats),
        avg_line_pct=sum(s["line_pct"] for s in stats) / len(stats) if stats else 0,
    )
    html_path.write_text(html_content, encoding="utf-8")
