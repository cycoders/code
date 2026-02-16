import sys
import logging
import typer
from pathlib import Path
from typing import Optional, List
from rich.logging import RichHandler
from .auditor import audit_page, batch_audit
from .reporter import Reporter
from .budget import PerfBudget
from .types import LighthouseResult

app = typer.Typer(no_args_is_help=True)
logging.basicConfig(level="INFO", format="%(message)s", handlers=[RichHandler()])


@app.command()
def audit(
    targets: List[str] = typer.Argument(..., show_default=False),
    budget: Optional[Path] = typer.Option(None, "--budget", help="Perf budget JSON"),
    html: Optional[Path] = typer.Option(None, "--html", help="HTML report"),
    json_out: Optional[Path] = typer.Option(None, "--json", help="JSON report"),
    compare: Optional[Path] = typer.Option(None, "--compare", help="Compare to prev JSON"),
    categories: List[str] = typer.Option(
        ["performance"], "--categories", help="Lighthouse categories"
    ),
):
    """Audit web vitals on URL(s) or local files. Supports @file for batch."""
    budget_obj = None
    if budget:
        budget_obj = PerfBudget.model_validate_json(budget.read_text())

    prev_result = None
    if compare:
        prev_result = LighthouseResult.model_validate_json(compare.read_text())

    # Handle batch file
    all_targets = []
    for t in targets:
        if t.startswith("@"):
            with open(t[1:], "r") as f:
                all_targets.extend(line.strip() for line in f if line.strip())
        else:
            all_targets.append(t)

    results = [audit_page(t, categories) for t in all_targets]
    result = results[0] if len(results) == 1 else None  # Single for reports

    reporter = Reporter(output=html)

    for r in results:
        reporter.terminal_report(r, budget_obj)

    if html and result:
        reporter.html_report(result, budget_obj, html)
    if json_out and result:
        reporter.json_report(result, json_out)
    if compare and result and prev_result:
        reporter.compare_reports(result, prev_result, budget_obj)

    if budget_obj and any(r for r in results):
        sys.exit(1 if any("fail" in evaluate_budget(r, budget_obj).values() for r in results) else 0)


if __name__ == "__main__":
    app()