from pathlib import Path
import shutil
from typing import List

from packaging.requirements import Requirement, InvalidRequirement

from .core import find_unused, AnalysisResult


def perform_prune(
    root: Path,
    req_file: Path,
    dry_run: bool = True,
    backup: bool = True,
) -> List[str]:
    """Prune unused from requirements.txt. Returns removed lines."""
    stats: AnalysisResult = find_unused(root, req_file)
    unused = stats['unused']

    if not unused:
        return []

    backup_path = req_file.with_suffix(req_file.suffix + '.orphan-deps-backup')
    if backup and not dry_run and backup_path.exists():
        backup_path.unlink()
    if backup and not dry_run:
        shutil.copy2(req_file, backup_path)

    lines = req_file.read_text(encoding='utf-8').splitlines(keepends=True)
    new_lines: List[str] = []
    removed: List[str] = []

    for line in lines:
        stripped = line.split('#')[0].strip()
        if not stripped:
            new_lines.append(line)
            continue
        try:
            pkg_name = Requirement(stripped).name.lower()
            if pkg_name in unused:
                removed.append(line.rstrip())
                continue
        except InvalidRequirement:
            pass
        new_lines.append(line)

    if dry_run:
        print('[yellow]DRY-RUN: Would remove:[/]')
        for r in removed:
            print(f'  {r}')
    else:
        req_file.write_text(''.join(new_lines), encoding='utf-8')
        print(f'[green]Pruned {len(removed)} deps. Backup: {backup_path}[/]')

    return [r.strip() for r in removed]