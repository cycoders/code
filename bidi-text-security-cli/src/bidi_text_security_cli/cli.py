from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .scanner import scan_file, Finding

console = Console()

@click.group()
def cli() -> None:
    """Unicode bidi attack scanner."""
    pass

@cli.command()
@click.argument("root", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json", "sarif"]))
@click.option("--fail-on", default="high")
def scan(root: Path, fmt: str, fail_on: str) -> None:
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".js", ".ts", ".go", ".rs", ".java", ".yaml", ".yml", ".json", ".toml", ".md"}:
            findings.extend(scan_file(path))
    if fmt == "text":
        _render_text(findings)
    elif fmt == "json":
        click.echo(json.dumps([f.__dict__ for f in findings], default=str))
    if any(f.risk == fail_on for f in findings):
        raise click.Abort()

def _render_text(findings: list[Finding]) -> None:
    if not findings:
        console.print("[green]No bidi characters found.[/]")
        return
    table = Table(title="Bidi Findings")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Char")
    table.add_column("Risk")
    for f in findings:
        table.add_row(str(f.path), str(f.line), f.name, f.risk)
    console.print(table)