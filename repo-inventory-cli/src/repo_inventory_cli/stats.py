import os
from collections import Counter
from pathlib import Path
from typing import List

from git import Repo, GitCommandError

from .models import RepoInfo


def compute_repo_stats(repo: Repo, rel_path: Path) -> RepoInfo:
    try:
        # Basic
        head = repo.head.commit
        last_commit_date = head.committed_datetime
        
        # Counts (fast git porcelain)
        commit_count = int(repo.git.rev_list("--count", "HEAD"))
        branch_count = len(repo.branches)
        remote_count = len(repo.remotes)
        
        # Status
        is_dirty = repo.is_dirty(untracked_files=True)
        current_branch = (
            repo.active_branch.name
            if repo.head.is_detached == False
            else "DETACHED"
        )
        
        # Size
        try:
            raw_size = int(repo.git.du("-sb", ".git").split()[0])
        except GitCommandError:
            raw_size = 0
        
        # Languages (top 3 exts)
        try:
            files_str = repo.git.ls_files("--format=%f")
            files = [f.strip() for f in files_str.splitlines() if f.strip()]
            exts = [Path(f).suffix.lstrip(".").lower() for f in files if Path(f).suffix]
            top_counter = Counter(exts).most_common(3)
            top_languages = [lang for lang, _ in top_counter]
        except:
            top_languages = []
        
        return RepoInfo(
            path=str(rel_path.relative_to(Path.cwd())),
            abs_path=str(rel_path),
            is_dirty=is_dirty,
            current_branch=current_branch,
            last_commit_date=last_commit_date,
            commit_count=commit_count,
            branch_count=branch_count,
            raw_git_size=raw_size,
            git_size=None,  # Set in table
            top_languages=top_languages,
            remote_count=remote_count,
        )
    except Exception:
        return None
