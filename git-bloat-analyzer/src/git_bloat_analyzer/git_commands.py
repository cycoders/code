import subprocess
from pathlib import Path
from typing import List


def run_git(args: List[str], repo_path: Path, capture_output: bool = True, text: bool = True) -> str:
    """Run git command in repo context."""
    cmd = ["git", "-C", str(repo_path), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=text,
            check=True,
            stderr=subprocess.STDOUT if not capture_output else None,
        )
        return result.stdout if text else result.stdout.decode()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {' '.join(cmd)} -> {e.stderr or e.stdout}") from e


def is_git_repo(repo_path: Path) -> bool:
    """Check if path is a Git repository."""
    try:
        run_git(["rev-parse", "--git-dir"], repo_path)
        return True
    except RuntimeError:
        return False