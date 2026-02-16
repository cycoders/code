import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .budget import evaluate_budget, print_budget_table
from .types import LighthouseResult, PerfBudget

console = Console()


class Reporter:
    def __init__(self, output: Optional[Path] = None, template_dir: str = "templates"):
        self.output = output
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape([
                "html",
                "xml",
            ]),
        )
        self.j2 = env

    def terminal_report(self, result: LighthouseResult, budget: Optional[PerfBudget] = None):
        table = Table(title="Lighthouse Results", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Score", justify="right")
        for cat, data in result.categories.items():
            table.add_row(cat.replace("-", " ").title(), f"{data['score']:.2f}")
        console.print(table)

        if budget:
            status = evaluate_budget(result, budget)
            print_budget_table(result, budget, status)

        # Top issues
        console.print("\n[bold]Top Opportunities:[/]")
        # Simplified: print audit details if low score
        low_audits = [
            k for k, v in result.audits.items() if v.get("score", 1) < 0.9
        ][:3]
        for audit in low_audits:
            console.print(f"• {audit.replace('-', ' ').title()}")

    def html_report(self, result: LighthouseResult, budget: Optional[PerfBudget] = None, path: Path):
        status = evaluate_budget(result, budget) if budget else {}
        template = self.j2.get_template("report.html")
        html = template.render(
            result=result.dict(), budget=budget.dict() if budget else {}, status=status
        )
        path.write_text(html)
        console.print(f"[green]HTML report saved: {path}[/]")

    def json_report(self, result: LighthouseResult, path: Path):
        path.write_text(json.dumps(result.dict(), indent=2))
        console.print(f"[green]JSON report saved: {path}[/]")

    def compare_reports(
        self, curr: LighthouseResult, prev: LighthouseResult, budget: Optional[PerfBudget]
    ):
        console.print("[bold yellow]Perf Delta (Current vs Previous)[/]")
        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Curr", justify="right")
        table.add_column("Prev", justify="right")
        table.add_column("Delta", justify="right")
        for mkey in curr.metrics:
            c_val = curr.metrics[mkey].numericValue
            p_val = prev.metrics.get(mkey, Metric(numericValue=float("inf"))).numericValue
            delta = c_val - p_val
            delta_str = f"{delta:+.0f}" if delta else "—"
            table.add_row(mkey.upper(), f"{c_val:.0f}", f"{p_val:.0f}", delta_str)
        console.print(table)
