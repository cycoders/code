from dataclasses import asdict
import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .types import FileRisk


console = Console()


def render_table(risks: List[FileRisk]) -> None:
    if not risks:
        rprint("[bold green]No overlapping changes. Merge safe![/] 🎉")
        return

    table = Table(title="[bold cyan]Merge Risk Analysis[/]")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Risk", style="bold magenta")
    table.add_column("Score", justify="right")
    table.add_column("Changes", justify="right")
    table.add_column("History", justify="right")
    table.add_column("Suggestion")

    for risk in risks:
        color = {"low": "green", "medium": "yellow", "high": "red"}[risk.risk_level]
        table.add_row(
            risk.path,
            f"[{color}]{risk.risk_level.upper()}[/]",
            f"{risk.risk_score:.3f}",
            f"{risk.change_size:,}",
            str(risk.historical_conflicts),
            risk.suggestion,
        )

    console.print(table)

    avg_score = sum(r.risk_score for r in risks) / len(risks)
    overall_level = "low" if avg_score < 0.3 else "medium" if avg_score < 0.7 else "high"
    color = {"low": "green", "medium": "yellow", "high": "red"}[overall_level]
    console.print(
        f"\n[bold {color}]{'Overall Risk: ' + overall_level.upper()} (avg: {avg_score:.3f})[/]"
    )


def render_json(risks: List[FileRisk]) -> None:
    data = [asdict(r) for r in risks]
    print(json.dumps(data, indent=2))
