import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from git import Repo
from git.exc import *

from .models import TodoItem


def get_blame_commit(repo: Repo, relpath: str, line: int) -> Optional['Commit']:
    """Get commit that last modified the given line via blame."""
    try:
        blame_iter = repo.blame('HEAD', relpath)
        for entry in blame_iter:
            start = entry.final_start_line_number
            end = start + entry.final_num_lines - 1
            if start <= line <= end:
                return entry.commit
    except GitCommandError:
        pass
    return None


def analyze_todos(
    todos: List[TodoItem],
    scan_root: str,
) -> List[TodoItem]:
    """Enrich todos with age and author from Git blame."""
    try:
        repo = Repo(os.path.dirname(scan_root), search_parent_directories=True)
        repo_root = Path(repo.working_tree_dir)
        scan_root_path = Path(scan_root).resolve()
        scan_root_rel = scan_root_path.relative_to(repo_root)
    except InvalidGitRepositoryError:
        return todos  # No Git, no ages

    now = datetime.now(timezone.utc)
    for todo in todos:
        try:
            full_rel = str(scan_root_rel / todo.filepath)
            commit = get_blame_commit(repo, full_rel, todo.line)
            if commit:
                authored = commit.authored_datetime.replace(tzinfo=timezone.utc)
                delta = now - authored
                todo.age_days = delta.total_seconds() / 86400.0
                todo.author = commit.author.name
        except (ValueError, GitCommandError, OSError):
            pass  # Skip invalid paths/commits
    return todos