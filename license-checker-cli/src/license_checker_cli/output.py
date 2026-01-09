import json
from typing import List, Any
from rich.console import Console
from rich.table import Table
from rich.json import JSONRenderer
from .models import LicenseInfo

console = Console()

PERMISSIVE_COLOR = "green"
COPYLEFT_COLOR = "red"
UNKNOWN_COLOR = "yellow"

COLOR_MAP = {
    "permissive": PERMISSIVE_COLOR,
    "copyleft": COPYLEFT_COLOR,
    "proprietary": "magenta",
    "unknown": UNKNOWN_COLOR,
}


def print_report(deps: List[LicenseInfo], fmt: str):
    if fmt == "json":
        console.print_json(data=[d.__dict__ for d in deps])
    elif fmt == "markdown":
        _print_markdown(deps)
    else:
        _print_table(deps)


def _print_table(deps: List[LicenseInfo]):
    table = Table(title="Dependency Licenses")
    table.add_column("Package", style="cyan")
    table.add_column("Version")
    table.add_column("License", style="magenta")
    table.add_column("Classification")
    table.add_column("Approved")

    for d in deps:
        color = COLOR_MAP.get(d.classification, UNKNOWN_COLOR)
        approved = "✅" if d.approved else "❌"
        table.add_row(
            d.name,
            d.version,
            d.license,
            d.classification or "unknown",
            approved,
            style=COLOR_MAP.get(d.classification),
        )
    console.print(table)


def _print_markdown(deps: List[LicenseInfo]):
    console.print("| Package | Version | License | Classification | Approved |")
    console.print("|---------|---------|---------|----------------|----------|")
    for d in deps:
        approved = "✅" if d.approved else "❌"
        console.print(f"| {d.name} | {d.version} | {d.license} | {d.classification or 'unknown'} | {approved} |")
