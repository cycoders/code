import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, List

from rich.progress import Progress
from rich.console import Console

from .utils import run_git, find_git_root


StatsEntry = Dict[str, Any]


def collect_large_file_stats(
    repo_path: Path,
    threshold_mb: float = 10.0,
) -> Dict[str, StatsEntry]:
    """Collect stats on large files across all commits, grouped by extension."""
    threshold_bytes = int(threshold_mb * 1024 * 1024)
    repo_path = find_git_root(repo_path)

    console = Console()

    commits_proc = run_git(["rev-list", "--all"], repo_path)
    commits = [c.strip() for c in commits_proc.stdout.strip().splitlines() if c.strip()]
    total_commits = len(commits)

    stats: Dict[str, StatsEntry] = defaultdict(lambda: {"count": 0, "total_size": 0, "paths": set()})

    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning Git history...", total=total_commits)
        for commit in commits:
            try:
                ls_proc = run_git(["ls-tree", "-r", "-l", "-t", commit], repo_path)
                for line in ls_proc.stdout.strip().splitlines():
                    parts = line.rsplit(maxsplit=4)
                    if len(parts) == 5 and parts[1] == "blob":
                        size = int(parts[3])
                        if size > threshold_bytes:
                            path = parts[4]
                            ext = Path(path).suffix.lower()
                            if not ext:
                                ext = f"noext-{Path(path).name[:8]}"
                            stats[ext]["count"] += 1
                            stats[ext]["total_size"] += size
                            stats[ext]["paths"].add(path)
            except subprocess.CalledProcessError:
                pass  # Skip unreachable commits
            progress.update(task, advance=1)

    # Convert defaultdict to dict
    return dict(stats)
