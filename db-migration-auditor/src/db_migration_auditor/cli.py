import typer
from pathlib import Path
from typing import Annotated, Optional

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .linter import lint_paths
from .models import Dialect, Issue, Severity

app = typer.Typer(add_completion=False)
console = Console()

SEVERITY_COLORS = {
    "error": "red",
    "warning": "yellow",
    "info": "green",
}

@app.command()
def lint(
    paths: Annotated[list[Path], typer.Argument(help="Files or dirs to lint")],
    dialect: Dialect = Dialect.POSTGRES,
    fmt: str = "table",
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Lint SQL migrations for risks."""
    all_issues = lint_paths(paths, dialect, verbose)

    if fmt == "json":
        import json
        data = [issue.model_dump() for issue in all_issues]
        result = json.dumps(data, indent=2)
    else:
        table = Table(title=f"Migration Audit ({dialect.value}): {len(all_issues)} issues")
        table.add_column("File")
        table.add_column("Line")
        table.add_column("Col")
        table.add_column("Severity", style="bold")
        table.add_column("Rule")
        table.add_column("Message")
        for issue in all_issues:
            color = SEVERITY_COLORS.get(issue.severity, "white")
            table.add_row(
                str(issue.file),
                str(issue.line),
                str(issue.col),
                issue.severity.upper(),
                issue.code,
                issue.message,
                style=color,
            )
        result = ""
        with console.capture() as capture:
            console.print(table)
        result = capture.get()

    if output:
        output.write_text(result)
        rprint(f"[green]Wrote report to {output}")
    else:
        print(result)

    if all_issues:
        raise typer.Exit(1)