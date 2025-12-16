import csv
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

import rich.console
import rich.table
from rich import box

from .models import TodoItem


console = rich.console.Console()


def report(
    todos: List[TodoItem],
    fmt: str = 'table',
    output: str = None,
) -> None:
    """Generate report in specified format."""
    if not todos:
        console.print("[green]No TODOs, FIXMEs, or HACKs found. Great job! 🎉[/green]")
        return

    todos.sort(key=lambda t: (t.age_days or 0, t.line), reverse=True)

    if fmt == 'csv':
        _export_csv(todos, output)
    elif fmt == 'mermaid':
        _export_mermaid(todos, output)
    else:
        _print_table(todos)


def _export_csv(todos: List[TodoItem], output: str) -> None:
    path = Path(output or 'todos.csv')
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['filepath', 'line', 'tag', 'age_days', 'author', 'message'])
        for t in todos:
            writer.writerow([t.filepath, t.line, t.tag, t.age_days, t.author, t.message])
    console.print(f"[green]CSV exported: {path}[/green]")


def _export_mermaid(todos: List[TodoItem], output: str) -> None:
    path = Path(output or 'todos.mmd')
    now = datetime.now(timezone.utc)
    lines = ['# Codebase Todos Timeline', '```mermaid', 'gantt', '    title Top 20 Oldest Todos',
             '    dateFormat  YYYY-MM-DD',
             '    todayMarker off']

    for i, todo in enumerate(todos[:20]):
        if todo.age_days:
            date_str = (now - timedelta(days=todo.age_days)).strftime('%Y-%m-%d')
            section = todo.tag
            task = f'{todo.message[:30]}'
            lines.append(f'    {task} :{section}, {date_str}, 1d')

    lines += ['```']
    path.write_text('\n'.join(lines))
    console.print(f"[green]Mermaid exported: {path}[/green]")


def _print_table(todos: List[TodoItem]) -> None:
    table = rich.table.Table(box=box.ROUNDED, title="[bold magenta]Todo Tracker Report[/bold magenta]")
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Line", justify="right", style="green")
    table.add_column("Tag", style="magenta", no_wrap=True)
    table.add_column("Age (days)", justify="right")
    table.add_column("Author", no_wrap=True)
    table.add_column("Message", overflow="fold")

    for todo in todos:
        age_str = f"{todo.age_days:.1f}" if todo.age_days is not None else "?"
        author_str = todo.author[:15] + '...' if todo.author and len(todo.author) > 15 else (todo.author or '?')
        table.add_row(
            todo.filepath[-45:] if len(todo.filepath) > 45 else todo.filepath,
            str(todo.line),
            todo.tag,
            str(age_str),
            author_str,
            todo.message[:100],
        )

    console.print(table)

    # Stats
    tag_counts = Counter(t.tag for t in todos)
    total = len(todos)
    console.print(f"\n[bold]Stats:[/bold] Total: {total}")
    for tag, count in tag_counts.most_common():
        pct = (count / total * 100)
        console.print(f"  [magenta]{tag}:[/magenta] {count} ({pct:.1f}%)"))