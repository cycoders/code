import json
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from .diff_engine import compute_diff
from .reporter import print_table_report

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Diff two OpenAPI specs and report changes.")
def diff(
    old_spec: typer.FileText = typer.Argument(..., help="Old OpenAPI spec (YAML/JSON)"),
    new_spec: typer.FileText = typer.Argument(..., help="New OpenAPI spec (YAML/JSON)"),
    output: str = typer.Option("table", "--output", "-o", help="Output: table (default), json"),
    json_out: Optional[typer.FileTextWrite] = typer.Option(None, "--json", "-j", help="Write JSON to file"),
    fail_fast: bool = typer.Option(False, "--fail-on-breaking", help="Exit 1 if breaking changes"),
):
    """Detect breaking/non-breaking changes between OpenAPI specs."""
    old_data = yaml.safe_load(old_spec)
    new_data = yaml.safe_load(new_spec)

    result = compute_diff(old_data, new_data)

    breaking_count = result["summary"]["breaking"]

    if fail_fast and breaking_count > 0:
        console.print(f"[bold red]❌ {breaking_count} breaking changes detected![/bold red]")
        raise typer.Exit(code=1)

    if json_out:
        json.dump(result, json_out, indent=2, default=str)
        console.print("[green]✓ JSON written[/green]")
    elif output == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        print_table_report(result)

if __name__ == "__main__":
    app(prog_name="openapi-diff")
