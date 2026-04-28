import git
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress

from .types import CommitInfo


def get_repo_commits(
    repo_path: Path,
    since: Optional[str] = None,
    until: Optional[str] = None,
    author: Optional[str] = None,
    no_merges: bool = False,
) -> List[CommitInfo]:
    repo = git.Repo(repo_path)

    kwargs: dict = {}
    if since:
        kwargs["since"] = since
    if until:
        kwargs["until"] = until
    if author:
        kwargs["author"] = author

    commits_iter = repo.iter_commits(no_merges=no_merges, **kwargs)

    commits: List[CommitInfo] = []
    with Progress() as progress:
        task = progress.add_task("[green]Loading commits...", total=None)
        for commit in commits_iter:
            progress.advance(task)
            try:
                stats = commit.stats
                authored_date = datetime.fromtimestamp(commit.authored_date)
                commits.append(
                    CommitInfo(
                        commit.hexsha[:8],
                        commit.author.name,
                        commit.author.email.lower(),
                        authored_date,
                        getattr(stats.total, "added", 0),
                        getattr(stats.total, "deleted", 0),
                        getattr(stats.total, "files", 0),
                    )
                )
            except Exception:
                # Skip commits without stats (e.g., pure config)
                pass
    return commits
