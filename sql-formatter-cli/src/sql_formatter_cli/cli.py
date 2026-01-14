'''CLI entrypoint.''' 

import sys
import glob
import os
import typer
import difflib
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

import sql_formatter_cli
from sql_formatter_cli.config import load_config
from sql_formatter_cli.formatter import format_sql

app = typer.Typer(add_completion=False)
console = Console()

@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def main(  # noqa: PLR0915
    paths: List[Path] = typer.Argument([], metavar="[PATH]", help="SQL files or directories"),
    recursive: bool = typer.Option(False, "-r/--recursive", help="Recurse into directories"),
    check: bool = typer.Option(False, "--check", help="Fail if changes needed"),
    diff: bool = typer.Option(False, "--diff", help="Show diffs"),
    in_place: bool = typer.Option(False, "-i/--in-place", help="Rewrite files"),
    config: str = typer.Option(None, "--config", help="Config file"),
    dialect: str = typer.Option(None, "--dialect", help="SQL dialect"),
    line_length: int = typer.Option(None, "--line-length", help="Max line length"),
    indent: str = typer.Option(None, "--indent", help="Indent unit"),
    keyword_case: str = typer.Option(None, "--keyword-case", help="UPPER/lower"),
    normalize: bool = typer.Option(None, "--normalize", help="Normalize identifiers"),
    quiet: bool = typer.Option(False, "-q/--quiet", help="No progress"),
):
    """Format SQL files or stdin."""
    overrides = {
        k: v
        for k, v in dict(
            dialect=dialect,
            line_length=line_length,
            indent=indent,
            keyword_case=keyword_case,
            normalize=normalize,
        ).items()
        if v is not None
    }
    config_dict = load_config(config, overrides)

    if not paths:
        # Stdin
        sql = sys.stdin.read()
        if not sql.strip():
            typer.Exit(0)
        try:
            formatted = format_sql(sql, config_dict)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e

        if sql == formatted:
            typer.Exit(0)
        if check:
            console.print("[red]stdin is not formatted[/red]")
            raise typer.Exit(1)
        if diff:
            sys.stdout.writelines(
                difflib.unified_diff(
                    sql.splitlines(keepends=True),
                    formatted.splitlines(keepends=True),
                    fromfile="stdin",
                    tofile="stdin",
                )
            )
        else:
            print(formatted, end="")
        return

    # Collect files
    sql_files: List[str] = []
    for path in paths:
        if path.is_dir():
            if not recursive:
                raise typer.BadParameter(f"'{path}' is a directory, use --recursive")
            sql_files.extend(
                glob.glob(str(path / "**/*.sql"), recursive=True)
                + glob.glob(str(path / "**/*.sq"), recursive=True)
            )
        else:
            if not path.exists():
                raise typer.BadParameter(f"'{path}' does not exist")
            if path.suffix.lower() not in {'.sql', '.sq'}:
                console.print(f"[yellow]Skipping non-SQL: {path}[/yellow]")
                continue
            sql_files.append(str(path))

    if not sql_files:
        console.print("[yellow]No SQL files found[/yellow]")
        raise typer.Exit(0)

    changed = False
    progress_columns = [TextColumn("[progress.description]{task.description}"), SpinnerColumn()]
    with (
        Progress(*progress_columns, console=console, transient=quiet) as progress
        if not quiet
        else typer.progressive_echo("")
    ):
        for filepath in sql_files:
            task_id = progress.add_task(f"{os.path.basename(filepath)}", total=None) if not quiet else None
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    sql = f.read()
                formatted = format_sql(sql, config_dict)

                if sql == formatted:
                    console.print(f"[green]✓[/green] {filepath}") if quiet else None
                    if task_id:
                        progress.advance(task_id)
                    continue

                changed = True
                if in_place:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(formatted)
                    console.print(f"[green]✓[/green] {filepath} (reformatted)")
                elif diff:
                    diff_lines = list(
                        difflib.unified_diff(
                            sql.splitlines(keepends=True),
                            formatted.splitlines(keepends=True),
                            fromfile=filepath,
                            tofile=filepath,
                        )
                    )
                    console.print("".join(diff_lines))
                else:
                    print(formatted)

                if task_id:
                    progress.advance(task_id)
            except Exception as e:
                console.print(f"[red]✗[/red] {filepath}: {e}", file=sys.stderr)
                changed = True

    if check and changed:
        console.print("[red]SQL not formatted (use --diff to see changes)[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
