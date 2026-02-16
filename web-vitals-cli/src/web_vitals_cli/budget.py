from typing import Dict
from rich import print as rprint
from rich.table import Table
from rich.emoji import Emoji
from .types import LighthouseResult, PerfBudget, Metric

EMOJI = {"pass": ":white_check_mark:", "warn": ":warning:", "fail": ":x:"}


def evaluate_budget(result: LighthouseResult, budget: PerfBudget) -> Dict[str, str]:
    """Evaluate metrics against budget. Returns status dict."""
    status = {}
    metrics = result.metrics

    # LCP (s)
    lcp_ms = metrics.get("lcp", Metric(displayValue="", numericValue=0)).numericValue / 1000
    status["LCP"] = "pass" if lcp_ms <= budget.lcp else "fail"

    # INP (ms)
    inp = metrics.get("inp", Metric(displayValue="", numericValue=0)).numericValue
    status["INP"] = "pass" if inp <= budget.inp else "fail"

    # CLS
    cls = metrics.get("cls", Metric(displayValue="", numericValue=0)).numericValue
    status["CLS"] = "pass" if cls <= budget.cls else "fail"

    # TTFB (ms)
    ttfb = metrics.get("ttfb", Metric(displayValue="", numericValue=0)).numericValue
    status["TTFB"] = "pass" if ttfb <= budget.ttfb else "fail"

    # FCP (s)
    fcp_ms = metrics.get("fcp", Metric(displayValue="", numericValue=0)).numericValue / 1000
    status["FCP"] = "pass" if fcp_ms <= budget.fcp else "fail"

    return status


def print_budget_table(result: LighthouseResult, budget: PerfBudget, status: Dict[str, str]):
    table = Table(title="Core Web Vitals", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Budget", style="yellow")
    table.add_column("Status", style="bold")

    for key in ["LCP", "INP", "CLS", "FCP", "TTFB"]:
        metric_key = key.lower()
        m = result.metrics.get(metric_key, Metric(displayValue="N/A", numericValue=float("inf")))
        val = m.displayValue
        bud = getattr(budget, metric_key, "N/A")
        stat = status.get(key, "unknown")
        emoji = EMOJI.get(stat, "?")
        table.add_row(key, val, f"≤{bud}", f"{emoji} {stat.upper()}")

    rprint(table)

    fails = [k for k, v in status.items() if v == "fail"]
    if fails:
        rprint(f"\n[bold red]❌ Fails: {', '.join(fails)}[/]")
    else:
        rprint("\n[bold green]✅ All PASS![/]")
