import subprocess
from pathlib import Path
from typing import List

from rich.console import Console

from .utils import run_git, find_git_root


console = Console()


def check_git_lfs_installed(repo_path: Path) -> None:
    """Ensure Git LFS is available."""
    repo_path = find_git_root(repo_path)
    try:
        run_git(["lfs", "version"], repo_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Git LFS not available: {e.stderr.strip()}.\nInstall with 'git lfs install' or https://git-lfs.com"
        )


def perform_migration(
    repo_path: Path,
    include_globs: str,
    dry_run: bool = True,
) -> str:
    """Run git lfs migrate import."""
    repo_path = find_git_root(repo_path)
    check_git_lfs_installed(repo_path)

    cmd = ["lfs", "migrate", "import", "--include", include_globs]
    if dry_run:
        cmd.insert(-1, "--dry-run")

    proc = run_git(cmd, repo_path)
    return proc.stdout
