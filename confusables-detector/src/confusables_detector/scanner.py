import os
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Generator, Any, Iterable

from rich.console import Console, ConsoleOptions
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import gitwildmatch

from .detector import normalize
from .highlighter import highlight_line


DEFAULT_IGNORES = [
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "build",
    "dist",
    ".tox",
    "__pycache__",
]

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".pyc",
    ".class",
    ".jar",
    ".bin",
}


def find_text_files(
    root: Path, ignores: List[str] = None
) -> Generator[Path, None, None]:
    """Yield text files, respecting ignores and binary ext."""
    all_ignores = DEFAULT_IGNORES + (ignores or [])
    spec_text = "\n".join(all_ignores)
    spec = PathSpec.from_lines(gitwildmatch, spec_text.splitlines())

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs
        dirpath_p = Path(dirpath)
        for dirname in dirnames[:]:  # copy
            if spec.match_file(dirpath_p / dirname):
                dirnames.remove(dirname)

        for filename in filenames:
            filepath = Path(dirpath) / filename
            relpath = filepath.relative_to(root).as_posix()
            if spec.match_file(relpath):
                continue
            if filepath.suffix.lower() in BINARY_EXTENSIONS:
                continue
            yield filepath


def process_file(filepath: Path, issues: List[Dict], stats: Dict[str, int]):
    """Process single file, update issues/stats."""
    try:
        text = filepath.read_text(errors="replace")
        lines = text.splitlines()
        stats["lines"] += len(lines)
        for lineno, line in enumerate(lines, 1):
            highlighted, count = highlight_line(line)
            if count > 0:
                issues.append(
                    {
                        "file": filepath,
                        "line": lineno,
                        "highlighted": highlighted,
                        "snippet": highlighted[:80] + "..." if len(highlighted) > 80 else highlighted,
                        "count": count,
                    }
                )
                stats["confusables"] += count
    except (UnicodeDecodeError, OSError):
        pass  # Skip unreadable
    stats["files"] += 1


def print_issues(console: Console, issues: List[Dict], root: Path):
    """Print issues table."""
    table = Table(
        "File",
        "Line",
        "Count",
        "Snippet",
        title="[bold red]Confusables Found[/bold red]",
        expand=True,
    )
    for issue in issues:
        rel_file = issue["file"].relative_to(root).as_posix()
        table.add_row(
            rel_file,
            str(issue["line"]),
            str(issue["count"]),
            issue["snippet"],
        )
    console.print(table)


def scan_directory(
    console: Console,
    root: Path,
    excludes: List[str],
    json_output: bool,
) -> Dict[str, Any]:
    """Main scan logic. Returns stats dict."""
    stats = defaultdict(int)
    issues: List[Dict] = []

    text_files = list(find_text_files(root, excludes))
    skipped = len(list(os.walk(root))) * 10  # rough est

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Scanning files...", total=len(text_files))
        for fp in text_files:
            process_file(fp, issues, stats)
            progress.advance(task)

    stats["skipped"] = skipped
    stats["issues"] = len(issues)
    total_conf = stats["confusables"]

    if not json_output:
        console.print(
            Panel(
                f"[green]✅[/green] Scanned [bold]{stats['files']}[/bold] files "
                f"([bold]{stats['skipped']}[/bold] skipped), [bold]{stats['lines']:,}[/bold] lines\n"
                f"[yellow]⚠️[/yellow]  Found [bold]{total_conf}[/bold] "
                f"confusables {'🎉 Clean!' if total_conf == 0 else '(low severity)'}",
                title="[bold blue]Scan Complete",
            )
        )

        if issues:
            print_issues(console, issues[:50], root)  # top 50
            if len(issues) > 50:
                console.print(f"... and {len(issues)-50} more", style="italic dim")

    return dict(stats)
