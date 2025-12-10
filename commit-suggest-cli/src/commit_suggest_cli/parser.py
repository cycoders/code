from typing import Dict, Any, List
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
import re
from pathlib import Path

def get_diff_text(repo_path: str, stage: str) -> str:
    """Fetch git diff text based on stage."""
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        raise ValueError(f"'{repo_path}' is not a valid git repository")

    if stage == "staged":
        return repo.git.diff("--cached")
    elif stage == "unstaged":
        return repo.git.diff()
    elif stage == "all":
        return repo.git.diff("HEAD")
    else:
        raise ValueError(f"Invalid stage: {stage}")

def parse_diff_text(diff_text: str) -> Dict[str, Any]:
    """Parse git diff text into structured changes."""
    changes: Dict[str, List[str]] = {"files": [], "added_lines": [], "removed_lines": []}

    file_pattern = re.compile(r"^diff --git a/([^\s]+) b/[^\s]+")
    lines = diff_text.splitlines()

    for line in lines:
        file_match = file_pattern.match(line)
        if file_match:
            changes["files"].append(file_match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            changes["added_lines"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            changes["removed_lines"].append(line[1:])

    return changes

def parse_diff(repo_path: str = ".", stage: str = "staged") -> Dict[str, Any]:
    """High-level: get diff and parse."""
    diff_text = get_diff_text(repo_path, stage)
    return parse_diff_text(diff_text)
