import subprocess
import re
from typing import List
from pathlib import Path

def _run_git(cmd: List[str], repo_path: Path, capture_output: bool = True) -> str:
    """Run git command, return stdout. Raises on error."""
    full_cmd = ["git", "-C", str(repo_path)] + cmd
    result = subprocess.run(
        full_cmd,
        capture_output=capture_output,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Git failed: {result.stderr or result.stdout}. Cmd: {' '.join(full_cmd)}"
        )
    return result.stdout.strip()

def get_merge_base(repo_path: Path, branch1: str, branch2: str) -> str:
    """
    Get the merge base commit hash between two branches.

    >>> get_merge_base(Path('.'), 'main', 'feature')
    'abc123'
    """
    return _run_git(["merge-base", branch1, branch2], repo_path)

def detect_conflicts(repo_path: Path, base: str, branch1: str, branch2: str) -> List[str]:
    """
    Detect conflicted files using git merge-tree. Returns list of conflicted paths.

    Parses output for conflict blocks: path\n<<<<<<<
    """
    out = _run_git(["merge-tree", base, branch1, branch2], repo_path)
    # Find conflicted paths: lines before \n<<<<<<< (MULTILINE)
    conflict_paths = re.findall(r"^([^\n]+)(?=\n<<<<<<<)", out, re.MULTILINE)
    return sorted(set(conflict_paths))  # dedup

def get_incoming_commits(repo_path: Path, source: str, target: str) -> List[str]:
    """
    Get list of incoming commits: git log source..target --oneline
    """
    log = _run_git(["log", "--oneline", f"{source}..{target}"], repo_path)
    return log.split("\n") if log else []

def get_current_graph(repo_path: Path, limit: int = 12) -> str:
    """
    Get current commit graph: git log --graph --oneline --decorate --all
    """
    return _run_git(
        ["log", "--graph", "--oneline", "--decorate", "--all", f"-n{limit}"], repo_path
    )

def get_conflict_diffs(repo_path: Path, path: str, base: str, branch1: str, branch2: str) -> tuple[str, str]:
    """
    Get unified diffs for conflicted file from base to each branch.
    """
    diff1 = _run_git(["diff", f"{base}..{branch1}", "--", path], repo_path)
    diff2 = _run_git(["diff", f"{base}..{branch2}", "--", path], repo_path)
    return diff1, diff2