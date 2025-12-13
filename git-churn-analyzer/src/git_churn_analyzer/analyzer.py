from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import tqdm

from .models import FileChurn, GitCommit


def analyze_commits(
    commits: list[GitCommit], recent_days: int = 30
) -> Dict[str, any]:
    """
    Compute churn stats from commits.

    Returns dict with top_files, top_authors, total_commits.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=recent_days)

    file_churn: Dict[str, FileChurn] = {}
    author_churn = Counter()

    for commit in tqdm.tqdm(commits, desc="Analyzing"):
        for change in commit.changes:
            path = change.path
            churn = change.lines_changed

            if path not in file_churn:
                file_churn[path] = FileChurn(path=path)

            fs: FileChurn = file_churn[path]
            fs.total_churn += churn
            fs.commit_count += 1
            fs.authors[commit.author] = fs.authors.get(commit.author, 0) + churn
            author_churn[commit.author] += churn

            if commit.timestamp is None or (fs.last_commit is None or commit.timestamp > fs.last_commit):
                fs.last_commit = commit.timestamp

            if commit.timestamp and commit.timestamp > cutoff:
                fs.recent_churn += churn

    # Compute top_author per file
    for fs in file_churn.values():
        if fs.authors:
            top_auth, top_churn = max(fs.authors.items(), key=lambda kv: kv[1])
            fs.top_author = top_auth
            fs.top_author_churn = top_churn

    top_files: List[FileChurn] = sorted(
        file_churn.values(), key=lambda f: f.total_churn, reverse=True
    )
    top_authors = author_churn.most_common(20)

    return {
        "top_files": top_files,
        "top_authors": top_authors,
        "total_commits": len(commits),
        "total_churn": sum(f.total_churn for f in file_churn.values()),
    }
