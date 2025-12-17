import csv
import json
import os
from typing import List, Dict

from rich.console import Console
from rich.table import Table


def report_results(
    results: List[Dict],
    fmt: str,
    output: str | None,
    console: Console,
):
    """Print/export results."""
    broken = [r for r in results if r["error"] or (r["status_code"] and r["status_code"] >= 400)]
    working = len(results) - len(broken)

    console.print(f"\n[bold green]✓ {working} working[/bold green]  [bold red]✗ {len(broken)} broken[/bold red]")

    if fmt == "table":
        _print_table(results, console)
    elif output:
        _export(output, results)


def _print_table(results: List[Dict], console: Console):
    results.sort(key=lambda r: (bool(r["error"] or (r["status_code"] and r["status_code"] >= 400)), r["url"]))
    table = Table(title="Link Audit Report", show_header=True, header_style="bold magenta")
    table.add_column("Status", style="dim", width=8)
    table.add_column("URL", max_width=70)
    table.add_column("Time", justify="right", width=8)
    table.add_column("Size KB", justify="right", width=9)
    table.add_column("Issues", max_width=30)

    for r in results:
        status = (
            "🟢"
            if r["status_code"] and 200 <= r["status_code"] < 400
            else "🔴" if r["status_code"] else "⚠️"
        )
        time_str = f"{r['response_time']:.2f}" if r["response_time"] else "-"
        size_str = f"{r['content_length']/1024:.1f}" if r["content_length"] else "-"
        issue = r["error"] or ("" if 200 <= r["status_code"] < 400 else f"HTTP {r['status_code']}")
        short_url = (r["url"][:67] + "...") if len(r["url"]) > 70 else r["url"]
        table.add_row(status, short_url, time_str, size_str, issue[:27])
    console.print(table)


def _export(output_path: str, results: List[Dict]):
    ext = os.path.splitext(output_path)[1][1:].lower()
    data = results
    if ext == "json":
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    elif ext == "csv":
        fields = ["url", "resolved_url", "status_code", "response_time", "content_length", "error"]
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    # MD export omitted for brevity
