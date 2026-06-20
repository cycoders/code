from __future__ import annotations

import json
import typer
from rich.console import Console
from rich.table import Table

from .detector import find_side_effects

app = typer.Typer(help="Detect side effects executed at import time.")
console = Console()

@app.command()
def main(
    path: str = typer.Argument(".", help="Python package or directory to scan"),
    fmt: str = typer.Option("rich", "--format", help="Output format: rich|json"),
    output: str | None = typer.Option(None, "--output", help="Write JSON report to file"),
):
    effects = find_side_effects(path)
    if fmt == "json":
        data = [e.__dict__ for e in effects]
        if output:
            with open(output, "w") as f:
                json.dump(data, f, indent=2)
        else:
            print(json.dumps(data, indent=2))
    else:
        table = Table(title="Detected Import Side Effects")
        table.add_column("Module")
        table.add_column("Line")
        table.add_column("Effect")
        table.add_column("Detail")
        for e in effects:
            table.add_row(e.module, str(e.line), e.kind, e.detail)
        console.print(table)
