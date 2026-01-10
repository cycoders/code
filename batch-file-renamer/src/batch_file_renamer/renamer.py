import os
import re
import shutil
import time
import json
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.progress import Progress, TextColumn
from rich.table import Table
from rich import box


def get_candidate_files(
    root: Path, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None
) -> List[Path]:
    """Collect candidate files matching include/exclude patterns."""
    files: List[Path] = []
    include = include or ["*"]
    exclude = exclude or []
    for path in root.rglob("*"):
        if path.is_file() and all(fnmatch.fnmatch(path.name, pat) for pat in include) \
           and not any(fnmatch.fnmatch(path.name, pat) for pat in exclude):
            files.append(path)
    return files


def sort_key(path: Path, sort_by: str) -> Any:
    """Get sort key for files."""
    if sort_by == "name":
        return path.name.lower()
    elif sort_by == "mtime":
        return path.stat().st_mtime
    elif sort_by == "size":
        return path.stat().st_size
    raise ValueError(f"Unknown sort_by: {sort_by}")


def apply_rule(current: str, rule: Dict[str, Any], extra: Dict[str, Any]) -> str:
    """
    Apply a single transformation rule to the current filename.

    Rules:
    - 'regex': {'pattern': re_pat, 'replacement': repl, 'ignorecase': bool}
    - 'prefix'/'suffix': {'value': str}
    - 'counter': {'fmt': '{:03d}', 'position': 'prefix'|'suffix'|'replace', 'start': int=1}
    - 'timestamp': {'fmt': '%Y%m%d_', 'stat': 'mtime'|'ctime'|'atime', 'position': str}
    """
    typ = rule["type"]

    if typ == "regex":
        flags = re.IGNORECASE if rule.get("ignorecase", False) else 0
        return re.sub(rule["pattern"], rule["replacement"], current, flags=flags)

    elif typ == "prefix":
        return rule["value"] + current

    elif typ == "suffix":
        return current + rule["value"]

    elif typ == "counter":
        start = rule.get("start", 1)
        n = extra["index"] + start
        fmt_str = rule["fmt"]
        generated = fmt_str.format(n=n)
        pos = rule.get("position", "prefix")
        if pos == "prefix":
            return generated + current
        elif pos == "suffix":
            return current + generated
        elif pos == "replace":
            return generated
        else:
            raise ValueError(f"Invalid counter position: {pos}")

    elif typ == "timestamp":
        attr = rule.get("stat", "mtime")
        stat_key = f"st_{attr}"
        t = getattr(extra["stat"], stat_key)
        fmt_str = rule["fmt"]
        generated = time.strftime(fmt_str, time.localtime(t))
        pos = rule.get("position", "prefix")
        if pos == "prefix":
            return generated + current
        elif pos == "suffix":
            return current + generated
        elif pos == "replace":
            return generated
        else:
            raise ValueError(f"Invalid timestamp position: {pos}")

    raise ValueError(f"Unknown rule type: {typ}")


def preview_renames(
    root: Path,
    rules: List[Dict[str, Any]],
    sort_by: str,
    include: Optional[List[str]],
    exclude: Optional[List[str]],
    console: Console,
) -> List[Dict[str, Any]]:
    """Compute proposed renames with conflict detection."""
    files = get_candidate_files(root, include, exclude)
    if not files:
        return []

    files.sort(key=lambda p: sort_key(p, sort_by))
    stat_cache = {p: p.stat() for p in files}
    renames = []

    for idx, old_path in enumerate(files):
        stat = stat_cache[old_path]
        extra = {
            "index": idx,
            "stem": old_path.stem,
            "suffix": old_path.suffix,
            "parent": old_path.parent.name,
            "stat": stat,
        }
        current = old_path.name
        for rule in rules:
            current = apply_rule(current, rule, extra)
        new_path = old_path.parent / current
        status = "conflict" if new_path.exists() and new_path != old_path else "ok"
        renames.append({"old": old_path, "new": new_path, "status": status, "stat": stat})
    return renames


def print_preview(renames: List[Dict[str, Any]], console: Console) -> None:
    """Print rich table preview."""
    if not renames:
        console.print("[yellow]No files to rename.[/]")
        return

    table = Table(box=box.ROUNDED, title="Rename Preview", show_header=True, header_style="bold magenta")
    table.add_column("Old", style="cyan")
    table.add_column("New", style="green")
    table.add_column("Status", style="bold")
    table.add_column("Size", justify="right")
    table.add_column("Modified", justify="right")

    conflicts = sum(1 for r in renames if r["status"] == "conflict")
    total = len(renames)

    for r in renames:
        row_style = "red" if r["status"] == "conflict" else "green"
        size = f"{r['stat'].st_size / 1024:.1f}k"
        modtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["stat"].st_mtime))
        table.add_row(
            r["old"].name,
            r["new"].name,
            r["status"].upper(),
            size,
            modtime,
            style=row_style,
        )

    console.print(table)
    console.print(f"[bold]{total} files, {conflicts} conflicts[/]")


def perform_apply(
    root: Path,
    renames: List[Dict[str, Any]],
    resolve_strategy: str,
    console: Console,
) -> None:
    """Perform the renames with backups and logging."""
    backups_dir = root / f".batch-file-renamer-backups-{time.strftime('%Y%m%d_%H%M%S')}"
    log: List[Dict[str, str]] = []

    with Progress(TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("[cyan]Renaming...", total=len(renames))
        for r in renames:
            old_path: Path = r["old"]
            new_path: Path = r["new"]
            if old_path == new_path:
                progress.advance(task)
                continue

            # Resolve conflict
            if new_path.exists():
                if resolve_strategy == "skip":
                    progress.advance(task)
                    continue
                elif resolve_strategy == "overwrite":
                    pass
                elif resolve_strategy == "append":
                    stem, suffix = new_path.stem, new_path.suffix
                    counter = 1
                    while (new_path := old_path.parent / f"{stem}_{counter}{suffix}").exists():
                        counter += 1

            backup_path = backups_dir / old_path.name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_path, backup_path)
            old_path.rename(new_path)
            log.append({
                "backup": str(backup_path),
                "old": str(old_path),
                "new": str(new_path),
            })
            progress.advance(task)

    log_path = root / ".batch-file-renamer-log.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    console.print(f"[green]Renamed {len(log)} files. Undo with: batch-file-renamer undo[/]")


def perform_undo(root: Path, console: Console) -> None:
    """Undo last rename batch from log and backups."""
    log_path = root / ".batch-file-renamer-log.json"
    if not log_path.exists():
        console.print("[red]No rename log found. Nothing to undo.[/]", err=True)
        raise typer.Exit(code=1)

    with open(log_path) as f:
        log: List[Dict[str, str]] = json.load(f)

    if not log:
        console.print("[yellow]Empty log.[/]")
        log_path.unlink(missing_ok=True)
        return

    backups_dir = Path(log[0]["backup"]).parent

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Undoing...", total=len(log))
        for entry in reversed(log):
            backup_path = Path(entry["backup"])
            old_path = Path(entry["old"])
            new_path = Path(entry["new"])

            if not backup_path.exists():
                console.print(f"[yellow]Backup missing for {old_path.name}, skipping.[/]", err=True)
                progress.advance(task)
                continue

            if old_path.exists():
                console.print(f"[yellow]Target {old_path.name} exists, skipping.[/]", err=True)
                progress.advance(task)
                continue

            shutil.move(backup_path, old_path)
            progress.advance(task)

    shutil.rmtree(backups_dir, ignore_errors=True)
    log_path.unlink(missing_ok=True)
    console.print("[green]Undo complete.[/]")