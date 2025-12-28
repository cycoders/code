from pathlib import Path
import sys
from typing import Optional

from git import Repo


def get_git_root(start_dir: Optional[Path] = None) -> Path:
    """
    Get the root of the git repository.

    Raises:
        RuntimeError: If not in a git repository.
    """
    start_dir = start_dir or Path.cwd()
    try:
        repo = Repo(str(start_dir), search_parent_directories=True)
        git_dir = repo.git_rev_parse("--git-dir")
        return Path(git_dir).parent
    except:
        raise RuntimeError("Must be run from within a Git repository")


def get_git_root_from_msg_file(msg_file: Path) -> Path:
    """
    Infer git root from COMMIT_EDITMSG path (.git/COMMIT_EDITMSG).
    """
    return msg_file.parent.parent
