from pathlib import Path
from typing import List
import json
import csv
from rich.console import Console
from rich.table import Table
from .types import AuditResult


console = Console()


def print_summary(results: List[AuditResult]) -> None:
    """Print high-level audit statistics."""
    total = len(results)
    ok = sum(1 for r in results if r.is_ok)
    broken = sum(1 for r in results if r.is_broken)
    errors = total - ok - broken
    times = [r.response_time for r in results if r.response_time is not None]
    avg_time = sum(times) / len(times) if times else 0.0
    slow = sum(1 for t in times if t > 2.0)

    summary_table = Table.grid(expand=True, padding=(0, 1))
    summary_table.add_row("[bold]Metric[/bold]", "[bold]Value[/bold]")
    summary_table.add_row("Total URLs", str(total))
    summary_table.add_row("✅ OK", str(ok))
    summary_table.add_row("❌ Broken", str(broken))
    summary_table.add_row("⚠️ Errors/5xx", str(errors))
    summary_table.add_row("🐌 Slow (>2s)", str(slow))
    summary_table.add_row("⏱️ Avg Time", f"{avg_time:.2f}s")
    console.print(summary_table)


def print_table(results: List[AuditResult]) -> None:
    """Print detailed results table."""
    table = Table(title="Detailed Audit Results", show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan", no_wrap=True)
    table.add_column("URL", no_wrap=True)
    table.add_column("Final URL")
    table.add_column("Time (s)", justify="right")
    table.add_column("Size (KB)", justify="right")
    table.add_column("Content-Type")

    for r in results:
        status_str = f"[green]{r.status_code}[/green]" if r.is_ok else f"[red]{r.status_code or r.error or 'ERROR'}[/red]"
        time_str = f"{r.response_time:.2f}" if r.response_time else "-"
        size_str = f"{r.size / 1024:.1f}" if r.size else "-"
        ct_str = r.content_type or "-"
        final_str = r.final_url or "-"
        table.add_row(status_str, r.url, final_str, time_str, size_str, ct_str)

    console.print(table)


def report_to_file(results: List[AuditResult], fmt: str, path: Path) -> None:
    """Export results to file in specified format."""
    data = [r.model_dump(exclude_none=True) for r in results]
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        path.write_text(json.dumps(data, indent=2) + "\n")
    elif fmt == "csv":
        if not path.suffix:
            path = path.with_suffix(".csv")
        with path.open("w", newline="", encoding="utf-8") as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0])
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerow(["url", "status_code", "error"])  # header
    elif fmt == "html":
        rows_html = "".join(
            f'<tr><td>{d.get("status_code", d.get("error", "ERR"))}</td><td>{d["url"]}</td><td>{d.get("final_url", "-")}</td><td>{d.get("response_time", "-")}</td></tr>'
            for d in data
        )
        html_content = f"""<!DOCTYPE html>
<html><head><title>Sitemap Audit Report</title><style>body{{font-family:Arial;}}table{{border-collapse:collapse;width:100%;}}th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}th{{background:#f2f2f2;}}</style></head>
<body><h1>Sitemap Audit ({len(data)} URLs)</h1>{rows_html}</table></body></html>
        """
        path.write_text(html_content)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Use table|json|csv|html.")