import typer
from pathlib import Path
from typing import List

import rich.console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .analyzer import analyze_directory, Violation


app = typer.Typer(no_args_is_help=True)
console = rich.console.Console()


@app.command(help="Scan Python files for perf pitfalls")
def scan(
    paths: List[Path] = typer.Argument(
        Path("."), help="Paths to scan (default: cwd)"
    ),
    ignore_dirs: List[str] = typer.Option([], "--ignore-dir"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
    json: bool = typer.Option(False, "--json"),
):
    """Scan directories/files for performance issues."""
    if not paths:
        paths = [Path.cwd()]

    all_violations: dict[Path, list[Violation]] = {}
    total_files = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning Python files...", total=None)

        for path in paths:
            if path.is_dir():
                dir_violations = analyze_directory(
                    path, ignore_dirs=ignore_dirs, verbose=verbose
                )
                all_violations.update(dir_violations)
                total_files += sum(1 for _ in dir_violations)
            else:
                try:
                    file_violations = analyze_file(path)
                    all_violations[path] = file_violations
                    total_files += 1
                except Exception as e:
                    if verbose:
                        console.print(f"[red]Error scanning {path}: {e}")
            progress.advance(task)

    total_issues = sum(len(vs) for vs in all_violations.values())
    console.print(
        f"[green]✅ {total_files} files scanned, {total_issues} issues found[/green]"
    )

    if total_issues == 0:
        return

    if json:
        import json

        flat = [
            {
                "file": str(f),
                "lineno": v.lineno,
                "col": v.col_offset,
                "rule": v.rule,
                "severity": v.severity,
                "message": v.message,
                "suggestion": v.suggestion,
            }
            for f, vs in all_violations.items()
            for v in vs
        ]
        console.print(json.dumps(flat, indent=2))
        return

    table = Table(title="Performance Pitfalls")
    table.add_column("File", style="cyan")
    table.add_column("Line", justify="right")
    table.add_column("Severity", style="bold magenta")
    table.add_column("Rule")
    table.add_column("Issue & Fix")

    for file_path, violations in sorted(all_violations.items()):
        for v in sorted(violations, key=lambda x: ("HIGH", "MED", "LOW").index(x.severity)):
            fix = f"[dim]({v.suggestion})[/dim]"
            table.add_row(
                str(file_path.relative_to(Path.cwd())),
                str(v.lineno),
                v.severity,
                v.rule.replace("-", " ").title(),
                f"{v.message} {fix}",
            )

    console.print(table)


if __name__ == "__main__":
    app()