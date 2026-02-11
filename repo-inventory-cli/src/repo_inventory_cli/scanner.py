import fnmatch
import os
from pathlib import Path
from typing import List, Iterator

from git import Repo, InvalidGitRepositoryError
from rich.progress import Progress, SpinnerColumn, TextColumn

from .models import RepoInfo
from .stats import compute_repo_stats


def scan_repos(paths: List[str], excludes: List[str]) -> List[RepoInfo]:
    repos: List[RepoInfo] = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Scanning for Git repos...", total=None)
        
        for base_path_str in paths:
            base_path = Path(base_path_str).expanduser().resolve()
            if not base_path.exists():
                continue
                
            for root, dirs, _ in os.walk(base_path):
                root_path = Path(root)
                
                # Prune excluded dirs
                if any(fnmatch.fnmatch(root, excl) for excl in excludes):
                    dirs[:] = []
                    continue
                
                git_dir = root_path / ".git"
                if git_dir.exists():
                    try:
                        repo = Repo(root, search_parent_directories=False)
                        repo_info = compute_repo_stats(repo, root_path)
                        if repo_info:
                            repos.append(repo_info)
                        progress.advance(task)
                    except InvalidGitRepositoryError:
                        pass
                    except Exception:
                        # Gracefully skip corrupted
                        pass
        progress.remove_task(task)
    
    return repos
