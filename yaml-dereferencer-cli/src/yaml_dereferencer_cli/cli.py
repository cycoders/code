import typer
from pathlib import Path
from typing_extensions import Annotated
import sys

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from .resolver import (
    resolve_yaml,
    validate_yaml,
    get_sharing_stats,
    ResolutionError,
    CycleError,
)

app = typer.Typer(help="YAML Dereferencer CLI", add_completion=False)
console = Console()

@app.command(help="Resolve anchors/aliases/merges to flat YAML")
def resolve(
    input_path: Path = typer.Argument(Path("-"), help="Input YAML"),
    output: Path = typer.Option(Path("deref.yaml"), "-o", help="Output path"),
    inplace: bool = typer.Option(False, "--inplace", help="Overwrite input"),
    stats: bool = typer.Option(False, "--stats", help="Show sharing stats"),
):
    try:
        with Progress(SpinnerColumn(), TextColumn("Dereferencing..."), console=console) as progress:
            task = progress.add_task("Load & resolve", total=None)
            data = validate_yaml(input_path.read_text())
            derefed = resolve_yaml(data)
            progress.remove_task(task)

        out_path = input_path if inplace else output
        out_path.write_text(derefed)
        rprint(f"[green]✓[/] Wrote {len(derefed)} chars to {out_path}")

        if stats:
            _show_stats(input_path.read_text())

    except ResolutionError as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(1) from e

@app.command(help="Rich side-by-side diff original vs dereferenced")
def diff(
    input_path: Path = typer.Argument(..., help="Input YAML"),
    html: Path = typer.Option(None, "--html", help="Save HTML diff"),
    context: int = typer.Option(3, "--context", min=0, max=20),
):
    try:
        orig = input_path.read_text()
        data = validate_yaml(orig)
        derefed_yaml = resolve_yaml(data)

        import difflib
diff_lines = list(
    difflib.unified_diff(
        orig.splitlines(keepends=True),
        derefed_yaml.splitlines(keepends=True),
        fromfile=str(input_path),
        tofile="dereferenced",
        n=context,
    )
)

        if html:
            from rich.console import RenderableType
            html_content = console.export_html(doc=diff_lines)
            html.write_text(f'''<!DOCTYPE html><html><head><title>YAML Diff</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/rich+/rich.min.css"></head><body>{html_content}</body></html>''')
            rprint(f"[green]✓[/] HTML diff: {html}")
            return

        if not diff_lines:
            rprint("[green]No changes (already dereferenced)")
        else:
            for line in diff_lines:
                console.print(line, soft_wrap=True, crop=False)

    except ResolutionError as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Validate anchors, detect cycles/duplicates")
def validate(input_path: Path = typer.Argument(..., help="Input YAML")):
    try:
        validate_yaml(input_path.read_text())
        rprint("[green]✓[/] Valid YAML: no cycles or duplicate anchors")
    except ResolutionError as e:
        typer.echo(f"[red]Invalid:[/red] {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Show anchor sharing stats")
def stats(input_path: Path = typer.Argument(..., help="Input YAML")):
    _show_stats(input_path.read_text())

@typer.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    if version:
        from . import __version__
        print(f"yaml-dereferencer-cli {__version__}")
        raise typer.Exit()

if __name__ == "__main__":
    app(prog_name="yaml-dereferencer")