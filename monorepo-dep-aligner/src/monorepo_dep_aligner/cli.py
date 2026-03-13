import typer
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm

import monorepo_dep_aligner
from .parser import find_pyprojects, parse_package_deps
from .auditor import audit_deps
from .aligner import choose_aligned_spec, align_dep_in_package
from .types import PackageInfo


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Check for dependency inconsistencies")
def check(root: Path = typer.Argument(Path("."), exists=True, file_ok=False)):
    """Scan monorepo for conflicting dep versions."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning pyproject.toml...", total=None)
        pyprojects = find_pyprojects(root)
        progress.update(task, total=len(pyprojects))

        packages: list[PackageInfo] = []
        for i, pp in enumerate(pyprojects):
            deps = parse_package_deps(pp)
            if deps:
                packages.append({"path": pp, "deps": deps})
            progress.advance(task)

    conflicts = audit_deps(packages)

    if not conflicts:
        rprint("[green]✓ All dependencies consistent across", len(packages), "packages![/]")
        raise typer.Exit(0)

    table = Table(title="Dependency Conflicts")
    table.add_column("Dependency", style="cyan")
    table.add_column("Specs")
    table.add_column("# Packages")

    for dep, usages in sorted(conflicts.items()):
        specs = {
            spec
            for pkg in usages
            for spec in pkg["deps"].get(dep, [])
        }
        table.add_row(dep, ", ".join(sorted(specs)), str(len(usages)))

    console.print(table)
    rprint(
        f"\n[yellow]⚠ {len(conflicts)} conflicts across {len(packages)} packages.[/]\n"
        f"[dim]Tip: Run `align {root}` to fix.[/]"
    )
    raise typer.Exit(1)


@app.command(help="Align inconsistent deps")
def align(
    root: Path = typer.Argument(Path("."), exists=True, file_ok=False),
    dry_run: bool = typer.Option(True, "--dry-run/-n", help="Preview changes"),
    yes: bool = typer.Option(False, "--yes/-y", help="Auto-confirm (dangerous)"),
):
    """Detect & align conflicts to consistent versions."""

    with Progress(...) as progress:
        task = progress.add_task("Scanning...", total=None)
        pyprojects = find_pyprojects(root)
        packages = []
        for pp in pyprojects:
            deps = parse_package_deps(pp)
            if deps:
                packages.append({"path": pp, "deps": deps})
        progress.remove_task(task)

    conflicts = audit_deps(packages)
    if not conflicts:
        rprint("[green]✓ No conflicts to align.[/]")
        raise typer.Exit(0)

    updated_count = 0
    for dep, usages in sorted(conflicts.items()):
        all_specs = [
            spec for pkg in usages for spec in pkg["deps"].get(dep, [])
        ]
        new_spec = choose_aligned_spec(all_specs)
        rprint(f"\n[blue]{dep}[/]: align to [green]{new_spec}[/]")

        for pkg in usages:
            path = pkg["path"]
            if align_dep_in_package(path, dep, new_spec, dry_run):
                updated_count += 1
                status = "[green]UPDATED[/]" if not dry_run else "[dim]WOULD[/]"
                rprint(f"  {status} {path.relative_to(root)} ")

    mode = "[yellow]DRY-RUN[/]" if dry_run else "[green]APPLIED[/]"
    rprint(f"\n{updated_count} alignments {mode} ({len(conflicts)} deps)")
    if not dry_run:
        rprint("[dim]Backups: *.toml.bak[/]")


if __name__ == "__main__":
    app()