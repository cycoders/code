import json
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from .types import Violation


def should_fail(violations: List[Violation], fail_on: str) -> bool:
    if not violations:
        return False
    has_error = any(v.severity == "error" for v in violations)
    has_warning = any(v.severity == "warning" for v in violations)
    if fail_on == "error":
        return has_error
    return has_error or has_warning


def report(
    violations: List[Violation],
    console: Console,
    json_output: bool = False,
) -> None:
    if json_output:
        data = [{
            "file": str(v.file),
            "line": v.line,
            "from_layer": v.from_layer,
            "to_layer": v.to_layer,
            "severity": v.severity,
            "message": v.message,
        } for v in violations]
        print(json.dumps(data, indent=2))
        return

    if not violations:
        console.print("[green]✓ No violations found![/]")
        return

    table = Table(title="Boundary Violations")
    table.add_column("File", style="cyan")
    table.add_column("Line")
    table.add_column("From Layer")
    table.add_column("To Layer")
    table.add_column("Severity")
    table.add_column("Message")

    for v in violations:
        color = "red" if v.severity == "error" else "yellow"
        to_layer = v.to_layer or "third_party"
        table.add_row(str(v.file.name), str(v.line), v.from_layer, to_layer, v.severity.upper(), v.message, style=color)

    console.print(table)

    errors = len([v for v in violations if v.severity == "error"])
    warnings = len(violations) - errors
    console.print(f"[bold]{errors} errors, {warnings} warnings[/]")