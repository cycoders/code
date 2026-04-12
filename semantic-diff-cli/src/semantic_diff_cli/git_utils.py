'''Git repository utilities.''' 

import git
from pathlib import Path
from rich.console import Console

from .diff_engine import print_semantic_diff

console = Console()

BINARY_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe', '.dll', '.so', '.bin', '.wasm', '.deb', '.rpm', '.tar', '.gz'}

def is_likely_binary(filepath: str) -> bool:
    """Check if file is likely binary by extension."""
    return Path(filepath).suffix.lower() in BINARY_EXTS

def perform_git_semdiff(base: str, head: str, repo_path: Path, only_text: bool = False) -> None:
    """Perform semantic diff between two git revisions."""
    repo = git.Repo(repo_path)

    try:
        changed = repo.git.diff(base, head, '--name-only').splitlines()
        changed_files = [f.strip() for f in changed if f.strip()]
    except git.exc.GitCommandError as e:
        raise typer.BadParameter(f"Git diff failed: {e}")

    if not changed_files:
        console.print("[green]No changed files.[/]")
        return

    console.print(f"[bold green]Analyzing {len(changed_files)} files...[/]")

    has_semantic_changes = False
    for rel_path in changed_files:
        if only_text and is_likely_binary(rel_path):
            console.print(f"[dim]Skipping binary: {rel_path}[/]")
            continue

        try:
            content_base = repo.git.show(f"{base}:{rel_path}")
            content_head = repo.git.show(f"{head}:{rel_path}")
            print_semantic_diff(rel_path, content_base, content_head)
            has_semantic_changes = True
        except git.exc.GitCommandError as e:
            console.print(f"[yellow]Skipping {rel_path}: {e}[/]")

    if not has_semantic_changes:
        console.print("[bold green]No semantic changes found across files![/]")
