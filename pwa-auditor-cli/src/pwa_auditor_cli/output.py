from dataclasses import dataclass
from typing import List

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str
    points_awarded: int
    max_points: int


def print_results(results: List[CheckResult], console: Console, json_output: bool = False) -> None:
    if json_output:
        total_max = sum(r.max_points for r in results)
        score = (sum(r.points_awarded for r in results) / total_max * 100) if total_max > 0 else 0
        data = {
            "overall_score": round(score, 1),
            "total_points": sum(r.points_awarded for r in results),
            "max_points": total_max,
            "checks": [{
                "name": r.name,
                "passed": r.passed,
                "details": r.details,
                "points_awarded": r.points_awarded,
                "max_points": r.max_points,
            } for r in results],
        }
        console.print(json.dumps(data, indent=2))
        return

    total_max = sum(r.max_points for r in results)
    score = (sum(r.points_awarded for r in results) / total_max * 100) if total_max > 0 else 0

    table = Table(box=box.ROUNDED, title="PWA Audit Results", show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=True)
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Details")

    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        score_str = f"{r.points_awarded}/{r.max_points}"
        table.add_row(r.name, status, score_str, r.details)

    score_panel = Panel(
        f"[bold green]Overall Score: {score:.1f}%[/bold green]",
        style="bold green" if score >= 80 else "bold yellow" if score >= 50 else "bold red",
        expand=False,
    )

    console.print(table)
    console.print(score_panel)
