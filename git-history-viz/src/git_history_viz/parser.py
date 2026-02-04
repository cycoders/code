from typing import Dict, List, Set, Optional

from git import Repo
from git.exc import InvalidGitRepositoryError

from .types import CommitNode


def parse_repo(
    repo_path: str, refs: Optional[List[str]], max_commits: int
) -> Dict[str, CommitNode]:
    """
    Parse Git repo into commit graph nodes.

    Traverses refs, deduplicates, limits count.
    """
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError as exc:
        raise ValueError(f"Invalid Git repository: {repo_path}") from exc

    if not repo.refs:
        return {}

    refs = refs or ["HEAD"]
    seen: Set[str] = set()
    commit_map: Dict[str, CommitNode] = {}
    count = 0

    for ref in refs:
        try:
            for commit in repo.iter_commits(ref, max_count=max_commits):
                sha = commit.hexsha
                if sha in seen or count >= max_commits:
                    break
                seen.add(sha)
                count += 1

                parents = [p.hexsha for p in commit.parents]
                first_line = commit.message.splitlines()[0].strip()[:60] or "(no message)"

                node = CommitNode(
                    sha=sha,
                    short_sha=sha[:8],
                    message=first_line,
                    author=commit.author.name,
                    date=commit.authored_datetime.strftime("%Y-%m-%d"),
                    parents=parents,
                )
                commit_map[sha] = node
        except Exception:
            # Skip invalid ref
            continue

    return commit_map
