import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models import FileChurn


console = Console()


def print_terminal(stats: Dict[str, Any]):
    """Rich terminal report."""
    rprint("[bold blue]Git Churn Analysis[/bold blue]")
    rprint(f"[dim]Analyzed {stats['total_commits']} commits | Total churn: {stats['total_churn']:,}[/]")

    table = Table(title="[bold]Top 20 Files by Total Churn[/bold]")
    table.add_column("Path", max_width=50)
    table.add_column("Total", justify="right")
    table.add_column("Recent (30d)", justify="right")
    table.add_column("Commits", justify="right")
    table.add_column("Last", justify="right", no_wrap=True)
    table.add_column("Top Author", max_width=15)

    for churn_file in stats["top_files"][:20]:
        last_str = (
            churn_file.last_commit.strftime("%Y-%m-%d")
            if churn_file.last_commit
            else "N/A"
        )
        top_auth = churn_file.top_author or "N/A"
        table.add_row(
            churn_file.path,
            str(churn_file.total_churn),
            str(churn_file.recent_churn),
            str(churn_file.commit_count),
            last_str,
            top_auth,
        )

    console.print(table)

    # Top authors
    auth_table = Table(title="Top Authors by Churn")
    auth_table.add_column("Author", max_width=20)
    auth_table.add_column("Churn", justify="right")
    for author, ch in stats["top_authors"][:10]:
        auth_table.add_row(author, str(ch))
    console.print(auth_table)


def write_csv(out_path: Path, stats: Dict[str, Any]):
    """CSV export."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["path", "total_churn", "recent_churn", "commit_count", "last_commit", "top_author"]
        )
        for fchurn in stats["top_files"]:
            writer.writerow([
                fchurn.path,
                fchurn.total_churn,
                fchurn.recent_churn,
                fchurn.commit_count,
                fchurn.last_commit.isoformat() if fchurn.last_commit else "",
                fchurn.top_author or "",
            ])


def write_json(out_path: Path, stats: Dict[str, Any]):
    """JSON export."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(stats, default=str, indent=2)
    out_path.write_text(content)


def write_html(out_path: Path, stats: Dict[str, Any]):
    """Simple HTML report."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Git Churn Report</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Git Churn Analysis Report</h1>
    <p><strong>Commits analyzed:</strong> {stats['total_commits']} | <strong>Total churn:</strong> {stats['total_churn']:,}</p>

    <h2>Top Files by Churn</h2>
    <table>
        <thead>
            <tr><th>Path</th><th>Total Churn</th><th>Recent (30d)</th><th>Commits</th><th>Last Commit</th><th>Top Author</th></tr>
        </thead>
        <tbody>
"""
    for fchurn in stats["top_files"][:50]:
        last_str = fchurn.last_commit.strftime("%Y-%m-%d") if fchurn.last_commit else "N/A"
        html += f"            <tr><td>{fchurn.path}</td><td>{fchurn.total_churn}</td><td>{fchurn.recent_churn}</td><td>{fchurn.commit_count}</td><td>{last_str}</td><td>{fchurn.top_author or ''}</td></tr>\n"
    html += """
        </tbody>
    </table>

    <h2>Top Authors</h2>
    <ul>
"""
    for author, ch in stats["top_authors"][:20]:
        html += f"        <li>{author}: {ch}</li>\n"
    html += """
    </ul>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
</body>
</html>
    """
    out_path.write_text(html)


def render_stats(stats: Dict[str, Any], fmt: str, out_path: Path):
    """Dispatch to renderer."""
    if str(out_path) != "-" and fmt == "terminal":
        rprint("[yellow]Terminal output to stdout only. Use --output -[/yellow]")
        out_path = Path("-")

    match fmt:
        case "terminal":
            print_terminal(stats)
        case "json":
            write_json(out_path, stats)
        case "csv":
            write_csv(out_path, stats)
        case "html":
            write_html(out_path, stats)
        case _:
            raise ValueError(f"Unsupported format: {fmt}")
