import typer
from pathlib import Path
from typing import Dict, Any

from rich.console import Console
from rich.table import Table

import unicode_normalizer_cli
from .scanner import scan_for_normalization
from .normalizer import needs_normalization
from .gitops import GitOps

app = typer.Typer(add_completion=False)
console = Console()

def print_issues_table(issues: Dict[Path, Dict[str, Any]], title: str = "Unicode Normalization Issues"):
    table = Table(title=title)
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Size Δ", justify="right")
    table.add_row("Preview", "")

    for path, issue in issues.items():
        content_len = len(issue["content"]) if issue.get("content_needs") else 0
        norm_len = len(issue["normalized_content"])
        size_delta = f"{norm_len - content_len:+,}B"
        typ = issue["type"]
        preview = "name" if issue["name_needs"] else "content[:50]"
        table.add_row(str(path.relative_to(Path.cwd())), typ, size_delta, preview)

    console.print(table)
    console.print(f"\n[bold]Found {len(issues)} issues.[/bold]")

@app.command()
def version():
    """Show version."""
    typer.echo(f"unicode-normalizer-cli {unicode_normalizer_cli.__version__}")

@app.command()
def scan(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False),
    form: str = typer.Option("NFC", "--form", help="NFC|NFD|NFKC|NFKD"),
    max_size: int = typer.Option(10_485_760, "--max-size", help="Max file size (bytes, ~10MB)"),
):
    """Scan directory for Unicode normalization issues."""
    issues = scan_for_normalization(path, form, max_size)
    if not issues:
        typer.echo("✅ No normalization issues found!")
        raise typer.Exit(0)
    print_issues_table(issues)

@app.command()
def normalize(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False),
    form: str = typer.Option("NFC", "--form"),
    dry_run: bool = typer.Option(True, "--dry-run"),
    in_place: bool = typer.Option(..., "--in-place", help="Apply changes (implies no dry-run)"),
    git_add: bool = typer.Option(False, "--git-add"),
    git_commit: str = typer.Option(None, "--git-commit"),
    max_size: int = typer.Option(10_485_760, "--max-size"),
):
    """Normalize files (dry-run by default)."""
    if dry_run and in_place:
        raise typer.BadParameter("--in-place cannot be used with --dry-run")
    if (git_add or git_commit) and not Path(path / ".git").exists():
        raise typer.BadParameter(f"{path} is not a Git repo")

    issues = scan_for_normalization(path, form, max_size)
    if not issues:
        typer.echo("✅ No issues to normalize!")
        raise typer.Exit(0)

    typer.echo("Preview:")
    print_issues_table(issues)

    if dry_run:
        typer.echo("\n👀 Dry-run complete. Use --in-place to apply.")
        raise typer.Exit(0)

    git: GitOps | None = None
    if git_add or git_commit:
        git = GitOps(path)

    affected_paths: list[str] = []
    for orig_path, issue in issues.items():
        current_path = orig_path
        if issue["name_needs"]:
            new_name, _ = needs_normalization(orig_path.name, form)
            new_path = orig_path.parent / new_name
            if new_path != current_path:
                if git:
                    git.repo.git.mv(str(current_path), str(new_path))
                current_path.rename(new_path)
                current_path = new_path
        if issue["content_needs"]:
            norm_content = issue["normalized_content"]
            current_path.write_text(norm_content, "utf-8")
            affected_paths.append(str(current_path))

    if git:
        if affected_paths:
            git.repo.index.add(set(affected_paths))
        if git_commit:
            git.repo.index.commit(git_commit)

    typer.echo("✅ Normalization applied and staged!")

if __name__ == "__main__":
    app()