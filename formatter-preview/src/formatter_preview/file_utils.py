import subprocess
from pathlib import Path
from typing import List

from rich.console import Console

console = Console()

PRETTIER_EXTS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".jsonc",
    ".css",
    ".scss",
    ".less",
    ".md",
    ".html",
    ".yaml",
    ".yml",
}
SUPPORTED_EXTS = {".py", ".pyi"} | PRETTIER_EXTS


def get_candidate_files(staged: bool = False, all_files: bool = False) -> List[str]:
    """
    Get Python/JS files from git status.

    --staged: git diff --cached
    --all: git ls-files
    default: git diff (unstaged)
    """
    exts = " ".join(f"*.{e.lstrip('.')}" for e in SUPPORTED_EXTS)

    try:
        if all_files:
            cmd = ["git", "ls-files", exts]
        elif staged:
            cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=AM", exts]
        else:
            cmd = ["git", "diff", "--name-only", "--diff-filter=AMU", exts]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(
            "[yellow]Not a git repo or git unavailable. Pass files explicitly.[/yellow]"
        )
        return []
