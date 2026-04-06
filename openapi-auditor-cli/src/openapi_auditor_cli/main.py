import json
import sys
from pathlib import Path
from typing import Dict

import typer
from rich.progress import Progress

from .auditor import Auditor
from .models import Issue
from .reporter import report_console, report_json, generate_html, generate_markdown
from .resolver import load_spec, deref_spec


app = typer.Typer(name="openapi-auditor", help="Comprehensive OpenAPI spec auditor.")


@app.command()
def main(
    spec: Path = typer.Argument(..., help="Path to OpenAPI spec (YAML/JSON)"),
    output: str = typer.Option("console", "--output", "-o", help="Output: console | json | markdown | html"),
    fail_level: str = typer.Option("error", "--fail-level", help="Fail on: error (default) | warn | info"),
):
    """Audit an OpenAPI specification for issues."""
    if not spec.exists():
        typer.echo(f"❌ Spec not found: {spec}", err=True)
        raise typer.Exit(code=1)

    with Progress() as progress:
        task = progress.add_task("[cyan]Loading & resolving...", total=None)

        try:
            spec_dict = load_spec(spec)
            progress.update(task, description="[green]Deref...")
            resolved = deref_spec(spec_dict)
            progress.update(task, description="[blue]Auditing...")
            auditor = Auditor()
            issues: list[Issue] = auditor.audit(resolved)
            progress.remove_task(task)
        except Exception as e:
            typer.echo(f"❌ Audit failed: {str(e)}", err=True)
            raise typer.Exit(code=1)

    # Report
    if output == "console":
        report_console(issues)
    elif output == "json":
        typer.echo(report_json(issues))
    elif output == "markdown":
        typer.echo(generate_markdown(issues))
    elif output == "html":
        html = generate_html(issues)
        out_path = spec.with_suffix(".audit.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        typer.echo(f"📄 HTML report: {out_path}")
    else:
        typer.echo(f"❌ Invalid output: {output}", err=True)
        raise typer.Exit(code=1)

    # Fail check
    severities: Dict[str, int] = {"error": 3, "warn": 2, "info": 1}
    fail_sev = severities.get(fail_level, 3)
    max_sev = max((severities.get(i.severity, 0) for i in issues), default=0)
    if max_sev >= fail_sev:
        typer.echo("❌ Audit failed threshold.", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
