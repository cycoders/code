import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any
import typer
from rich.progress import Progress
from .utils import run_git

def parse_worktree_list(output: str) -> List[Dict[str, Any]]:
    """Parse `git worktree list --porcelain` into dicts."""
    worktrees: List[Dict[str, Any]] = []
    blocks = output.split("\n\n")
    for block in blocks:
        if not block.strip():
            continue
        wt: Dict[str, Any] = {}
        for line in block.splitlines():
            if line.startswith("worktree "):
                wt["path"] = line.split(maxsplit=1)[1]
            elif line.startswith("headrefs "):
                wt["headrefs"] = line[9:]
            elif line.startswith("bare"):
                wt["bare"] = True
            elif line.startswith("locked "):
                wt["locked"] = line[7:]
        if wt:
            worktrees.append(wt)
    return worktrees

def get_worktree_status(path: Path) -> Dict[str, Any]:
    """Compute branch, ahead/behind, dirty from `git status --porcelain=v2 --branch`."""
    cwd = str(path)
    try:
        status_out = run_git("status", "--porcelain=v2", "--branch", cwd=cwd)
    except RuntimeError:
        return {"branch": "error", "ahead": 0, "behind": 0, "dirty": 0}
    lines = status_out.splitlines()
    branch_line = None
    dirty_count = sum(1 for line in lines if not line.startswith("# "))
    for line in lines:
        if line.startswith("# branch."):
            branch_line = line
            break
    if not branch_line:
        return {"branch": "HEAD", "ahead": 0, "behind": 0, "dirty": dirty_count, "commit": ""}
    parts = branch_line.split()
    branch_name = parts[1]
    ahead, behind = 0, 0
    if len(parts) > 3 and parts[2] == "+" + str(parts[2][1:]):
        ahead = int(parts[2][1:])
        behind = int(parts[3][1:])
    commit_short = run_git("rev-parse", "--short=7", "HEAD", cwd=cwd)
    return {
        "branch": branch_name,
        "ahead": ahead,
        "behind": behind,
        "dirty": dirty_count,
        "commit": commit_short,
    }

def list_worktrees(config: dict) -> List[Dict[str, Any]]:
    """Full enriched worktree list."""
    output = run_git("worktree", "list", "--porcelain")
    raw_wts = parse_worktree_list(output)
    repo_root = Path(run_git("rev-parse", "--show-toplevel"))
    enriched = []
    with Progress() as progress:
        task = progress.add_task("[green]Computing status...", total=len(raw_wts))
        for wt in raw_wts:
            path = Path(wt["path"])
            wt.update(get_worktree_status(path))
            wt["rel_path"] = str(path.relative_to(repo_root)) if path.resolve() != repo_root.resolve() else "."
            if "locked" in wt:
                wt["status"] = f"locked: {wt['locked']}"
            enriched.append(wt)
            progress.advance(task)
    return enriched

def create_worktree(name: str, from_ref: str | None, config: dict):
    """Create worktree: mkdir, git worktree add -b."""
    core = config.get("core", {})
    base_dir_template = core.get("base_dir", "./worktrees/{name}")
    safe_name = name.replace("/", "-").replace(" ", "-")
    path = base_dir_template.format(name=safe_name)
    Path(path).mkdir(parents=True, exist_ok=True)
    start_point = from_ref or core.get("default_from", "HEAD")
    run_git("worktree", "add", "-b", name, path, start_point)
    typer.echo(f"[green]✓[/] Created worktree '{name}' at [blue]{path}[/]")
    typer.echo(f"[dim]➜[/] cd [bold cyan]{path}[/] && git push -u origin {name}")

def switch_worktree(identifier: str, worktrees: List[Dict]):
    """Find and print cd for worktree."""
    for wt in worktrees:
        if wt["rel_path"].endswith(identifier) or wt.get("branch") == identifier or wt.get("headrefs", "").endswith(f"/ {identifier}"):
            typer.echo(f"[bold green]➜[/] cd [bold cyan]{wt['path']}[/] ({wt.get('branch', 'detached')})")
            raise typer.Exit(0)
    typer.echo(f"[!] Worktree '{identifier}' not found.", err=True)
    raise typer.Exit(1)

def prune_worktrees(dry_run: bool, stale_days: int, config: dict):
    """Prune logic: check branch existence + activity."""
    wts = list_worktrees(config)
    repo_root_path = Path(run_git("rev-parse", "--show-toplevel"))
    now = time.time()
    pruned = 0
    for wt in wts:
        path_str = wt["path"]
        if Path(path_str) == repo_root_path or wt.get("bare"):
            continue
        if wt.get("locked"):
            typer.echo(f"[yellow]Skip[/] locked: {wt['rel_path']}")
            continue
        remove = False
        reason = ""
        # Check remote branch
        headrefs = wt.get("headrefs", "")
        if headrefs.startswith("heads/"):
            local_br = headrefs[7:]
            remote_br = f"origin/{local_br}"
            try:
                run_git("branch", "-r", "--contains", wt["commit"], remote_br)
            except RuntimeError:
                remove = True
                reason = f"branch '{local_br}' gone remotely"
        # Check staleness
        try:
            last_ct = int(run_git("log", "-1", "--format=%ct", cwd=path_str))
            if now - last_ct > stale_days * 86400:
                remove = True
                reason = f"inactive {int((now - last_ct)/86400)}d"
        except (RuntimeError, ValueError):
            remove = True
            reason = "no commits/invalid"
        if remove:
            action = "[dry]" if dry_run else "[red]PRUNE[/]"
            typer.echo(f"{action} {wt['rel_path']} ({reason})")
            if not dry_run:
                run_git("worktree", "remove", path_str)
                pruned += 1
    if not dry_run:
        typer.echo(f"[green]✓[/] Pruned {pruned} worktrees.")

def is_git_repo() -> bool:
    try:
        run_git("rev-parse", "--git-dir")
        return True
    except RuntimeError:
        return False