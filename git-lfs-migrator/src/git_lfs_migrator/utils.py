import subprocess
from pathlib import Path
from typing import List


def find_git_root(start: Path = Path.cwd()) -> Path:
    """Find the root of the Git repository."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise ValueError(f"Not inside a Git repository (searched from {start})\n")


def run_git(args: List[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    """Run a Git command and return the result."""
    full_cmd = ["git"] + args
    proc = subprocess.run(
        full_cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )
    return proc
