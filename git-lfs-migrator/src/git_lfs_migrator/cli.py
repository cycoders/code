import typer
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from .scanner import collect_large_file_stats
from .suggester import suggest_globs
from .migrator import check_git_lfs_installed, perform_migration
from .utils import find_git_root


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Scan repo history for large files by extension")
def scan(
    threshold_mb: float = typer.Option(10.0, "-t", "--threshold", min=0.1),
    repo_path: Path = typer.Option(
        Path("."),
        "-r",
        "--repo",
        help="Git repo path",
        resolve_path=True,
        exists=True,
    ),
):
    repo = find_git_root(repo_path)
    check_git_lfs_installed(repo)

    stats = collect_large_file_stats(repo, threshold_mb)
    if not stats:
        console.print(f"[green]No files > {threshold_mb}MB found in history.[/]\n")
        raise typer.Exit(0)

    total_bytes = sum(s["total_size"] for s in stats.values())
    table = Table(
        title=f"[bold cyan]Large files (> {threshold_mb:.1f}MB)[/bold cyan]",
    )
    table.add_column("Extension", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right")
    table.add_column("Total Size", justify="right")
    table.add_column("Coverage", justify="right")
    table.add_column("Sample Paths", max_width=40)

    for ext in sorted(stats, key=lambda e: stats[e]["total_size"], reverse=True):
        s = stats[ext]
        pct = (s["total_size"] / total_bytes) * 100
        paths_str = ", ".join(list(s["paths"])[:3])
        table.add_row(
            ext,
            str(s["count"]),
            f"{s['total_size']/1024/1024:.1f}MB",
            f"{pct:.1f}%",
            paths_str,
        )

    console.print(table)
    console.print(f"\n[bold]Total bloat: {total_bytes/1024/1024:.1f}MB across {len(stats)} groups[/bold]\n")


@app.command(help="Suggest optimal globs for LFS migration")
def suggest(
    threshold_mb: float = typer.Option(10.0, "-t", "--threshold", min=0.1),
    top_k: int = typer.Option(10, "-k", "--top-k", min=1, max=50),
    coverage_target: float = typer.Option(0.95, "--coverage", min=0.5, max=1.0),
    repo_path: Path = typer.Option(
        Path("."),
        "-r",
        "--repo",
        help="Git repo path",
        resolve_path=True,
        exists=True,
    ),
):
    repo = find_git_root(repo_path)
    check_git_lfs_installed(repo)

    stats = collect_large_file_stats(repo, threshold_mb)
    if not stats:
        console.print("[yellow]No large files to suggest.[/]\n")
        raise typer.Exit(0)

    total_bytes = sum(s["total_size"] for s in stats.values())
    globs = suggest_globs(stats, coverage_target, top_k)

    table = Table(title="[bold cyan]Suggested LFS globs[/bold cyan]")
    table.add_column("Glob", style="green")
    table.add_column("Bytes Saved", justify="right")
    table.add_column("Cumulative", justify="right")
    table.add_row("---", "---", "---")

    cum_bytes = 0
    for glob in globs:
        ext = glob[1:]
        entry = stats[ext]
        inc_bytes = entry["total_size"]
        cum_bytes += inc_bytes
        cum_pct = (cum_bytes / total_bytes) * 100
        table.add_row(glob, f"{inc_bytes/1024/1024:.1f}MB", f"{cum_pct:.1f}%")

    console.print(table)
    console.print(f"\n[bold green]Copy-paste: '{','.join(globs)}' → covers {cum_bytes/total_bytes*100:.1f}%[/]\n")


@app.command(help="Migrate files to Git LFS")
def migrate(
    globs: List[str] = typer.Argument(None, help="Globs e.g. '*.png' '*.zip'"),
    auto_suggest: bool = typer.Option(False, "--auto-suggest"),
    threshold_mb: float = typer.Option(10.0, "-t", "--threshold"),
    dry_run: bool = typer.Option(True, "-n", "--dry-run"),
    repo_path: Path = typer.Option(
        Path("."),
        "-r",
        "--repo",
        help="Git repo path",
        resolve_path=True,
        exists=True,
    ),
):
    repo = find_git_root(repo_path)
    check_git_lfs_installed(repo)

    if auto_suggest:
        if globs:
            raise typer.BadParameter("--auto-suggest conflicts with GLobs")
        stats = collect_large_file_stats(repo, threshold_mb)
        globs = suggest_globs(stats)

    if not globs:
        raise typer.BadParameter("Provide globs or --auto-suggest")

    include = ",".join(globs)
    console.print(f"[bold yellow]Migrating with:[bold] {include} [dim](dry-run={'ON' if dry_run else 'OFF'})[/]\n")

    try:
        output = perform_migration(repo, include, dry_run)
        console.print(output)
        if not dry_run:
            console.print("\n[bold green]✅ Migration complete. Run 'git lfs ls-files' to verify.[/]\n")
    except RuntimeError as e:
        console.print(f"[red]✗ {e}[/]\n")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
