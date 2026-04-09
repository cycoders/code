import subprocess
import os
from typing import List, Tuple

def is_git_repo(cwd: str = ".") -> bool:
    """Check if cwd is a git repo."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_changed_files(base: str, head: str, cwd: str = ".") -> List[Tuple[str, str]]:
    """
    Run 'git diff --name-status base..head'.

    Returns: [(path, status), ...] where status in {A,M,D,R,C}
    """
    if not os.path.isdir(cwd):
        raise ValueError(f"Invalid cwd: {cwd}")

    cmd = ["git", "diff", "--name-status", base, head, "--"]
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except FileNotFoundError:
        raise ValueError("Git not found. Install git.")
    except subprocess.TimeoutExpired:
        raise ValueError("Git diff timed out (huge diff?).")

    changes: List[Tuple[str, str]] = []
    for line in result.stdout.strip().splitlines():
        if "\t" in line:
            status, *path_parts = line.split("\t")
            path = "\t".join(path_parts)  # Handle tabs in paths
            changes.append((path.strip(), status))
    return changes