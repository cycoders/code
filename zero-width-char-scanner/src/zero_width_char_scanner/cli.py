from __future__ import annotations
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .scanner import scan_file

app = typer.Typer()
console = Console()


@app.command()
def main(
    path: Path = typer.Argument(Path(".")),
    fmt: str = typer.Option("text", "--format", "-f"),
):
    findings = []
    for p in path.rglob("*"):
        if p.is_file():
            findings.extend(scan_file(p))
    if fmt == "json":
        print(json.dumps(findings, indent=2))
    elif fmt == "sarif":
        print(json.dumps({"version": "2.1.0", "runs": [{"results": findings}]}))
    else:
        table = Table("file", "offset", "category")
        for f in findings:
            table.add_row(f["file"], str(f["offset"]), f["category"])
        console.print(table)
