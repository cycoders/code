from typing import List

import rich.console
import rich.table
from rich import box

from .models import IndexSuggestion


def render_table(console: rich.console.Console, suggestions: List[IndexSuggestion], min_score: float = 20.0) -> None:
    high = [s for s in suggestions if s.score >= 50]
    low = [s for s in suggestions if 20 <= s.score < 50]
    if high:
        console.print("[bold green]High Impact Suggestions (Score >= 50):[/]")
        _render_suggestions(console, high)
    if low:
        console.print("\n[bold yellow]Medium Impact Suggestions:[/]")
        _render_suggestions(console, low)
    console.print(f"\nTotal suggestions: {len(suggestions)}. Run with --output json for full list.")


def _render_suggestions(console: rich.console.Console, suggestions: List[IndexSuggestion]) -> None:
    table = rich.table.Table(box=box.ROUNDED)
    table.add_column("Table", style="cyan")
    table.add_column("Index Columns", style="magenta")
    table.add_column("Score", justify="right")
    table.add_column("Rationale", style="green")
    table.add_column("SQL", style="white")
    for sug in suggestions:
        table.add_row(
            sug.table,
            ", ".join(sug.columns),
            f"{sug.score:.1f}",
            sug.rationale,
            sug.sql,
        )
    console.print(table)


def render_json(suggestions: List[IndexSuggestion]) -> str:
    import json

    data = [{
        "table": s.table,
        "columns": s.columns,
        "score": s.score,
        "rationale": s.rationale,
        "sql": s.sql,
    } for s in suggestions]
    return json.dumps(data, indent=2)
