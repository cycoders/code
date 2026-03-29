import typer
from pathlib import Path
from typing import Annotated, List

from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .analyzer import LoadedNamesVisitor, get_provided_names
from .optimizer import STDLIB_MODULES, classify, get_module_key, group_order, process_module
from .utils import find_python_files

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Scan files/directories for import issues")
def scan(
    paths: Annotated[List[Path], typer.Argument(path_validator=typer.File(...))] = [Path(".")],
    recursive: bool = typer.Option(True, "--recursive/-r", help="Recurse into directories"),
):
    stats = {}
    total_imports = 0
    total_unused = 0

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning...", total=None)
        for path_str in paths:
            for file_path in find_python_files(path_str, recursive):
                try:
                    code = file_path.read_text(encoding="utf-8")
                    module = cst.parse_module(code)
                    loaded_visitor = LoadedNamesVisitor()
                    loaded_visitor.visit(module)
                    loaded_names = loaded_visitor.loaded
                    top_imports = [
                        stmt for stmt in module.body
                        if isinstance(stmt, (cst.Import, cst.ImportFrom))
                    ]
                    provided = [(stmt, get_provided_names(stmt)) for stmt in top_imports]
                    unused_count = sum(
                        1 for stmt, names in provided
                        if names != {"__all__star__"} and not (names & loaded_names)
                    )
                    stats[str(file_path)] = {
                        "total": len(top_imports),
                        "unused": unused_count,
                        "clean_pct": 100 * (1 - unused_count / max(1, len(top_imports))),
                    }
                    total_imports += len(top_imports)
                    total_unused += unused_count
                except Exception as e:
                    console.print(f"[red]Failed to parse {file_path}: {e}")
                progress.advance(task)

    if not stats:
        console.print("[yellow]No Python files found.")
        raise typer.Exit(1)

    table = Table(title="Import Scan Results", box=box.ROUNDED)
    table.add_column("Path", style="cyan")
    table.add_column("Total Imports", justify="right")
    table.add_column("Unused", justify="right")
    table.add_column("Cleanliness", justify="right")

    for path, data in stats.items():
        table.add_row(
            path,
            str(data["total"]),
            str(data["unused"]),
            f"{data['clean_pct']:.1f}%",
        )

    overall_clean = 100 * (1 - total_unused / max(1, total_imports))
    console.print(table)
    console.print(
        f"\n[yellow]Summary:[/yellow] {total_imports} imports, {total_unused} unused ({overall_clean:.1f}% clean)"
    )


@app.command(help="Optimize imports (dry-run by default)")
def optimize(
    paths: Annotated[List[Path], typer.Argument(...)] = [Path(".")],
    dry_run: bool = typer.Option(True, "--dry-run/-n", help="Show diffs, don't write"),
    check: bool = typer.Option(False, "--check", help="Fail if changes needed"),
    recursive: bool = typer.Option(True, "--recursive/-r"),
    verbose: bool = typer.Option(False, "--verbose/-v"),
):
    changed_files = 0

    for file_path in find_python_files(paths[0] if paths else Path("."), recursive):
        try:
            original_code = file_path.read_text(encoding="utf-8")
            module = cst.parse_module(original_code)
            new_module = process_module(module)
            new_code = new_module.code

            if new_code != original_code:
                changed_files += 1
                if dry_run:
                    import difflib
                    diff = difflib.unified_diff(
                        original_code.splitlines(keepends=True),
                        new_code.splitlines(keepends=True),
                        fromfile=str(file_path),
                        tofile=str(file_path),
                    )
                    from rich.syntax import Syntax
                    console.print(Syntax("".join(diff), "diff", line_numbers=True, word_wrap=False))
                else:
                    file_path.write_text(new_code, encoding="utf-8")
                    if verbose:
                        console.print(f"[green]Optimized {file_path}")
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}")

    if changed_files > 0 and check:
        console.print("[red]Check failed: changes needed!")
        raise typer.Exit(1)
    console.print(f"[green]{changed_files} files {'would be ' if dry_run else ''}changed.")


def main():
    app()
