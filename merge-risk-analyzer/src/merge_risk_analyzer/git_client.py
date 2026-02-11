import git
from pathlib import Path
from typing import Set, Tuple


class GitClient:
    """
    Wrapper for GitPython operations with error handling.
    """

    def __init__(self, repo_path: Path):
        if not (repo_path / ".git").exists():
            raise ValueError(f"Not a Git repository: {repo_path}")
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)

    def resolve_ref(self, ref: str) -> str:
        """Resolve branch/tag/ref to commit SHA."""
        try:
            return (
                self.repo.rev_parse(ref).hexsha
                if ref not in [head.name for head in self.repo.heads]
                else self.repo.heads[ref].commit.hexsha
            )
        except git.exc.GitCommandError:
            raise ValueError(f"Cannot resolve reference '{ref}' in repo")

    def get_merge_base(self, source_ref: str, target_ref: str) -> str:
        """Get SHA of merge-base commit."""
        source_sha = self.resolve_ref(source_ref)
        target_sha = self.resolve_ref(target_ref)
        merge_bases = self.repo.git.merge_base(source_sha, target_sha)
        if not merge_bases:
            raise ValueError(
                f"No merge base between {source_ref} and {target_ref}; "
                "branches may not share ancestry."
            )
        return merge_bases.splitlines()[0]

    def get_changed_files(self, since: str, upto: str) -> Set[str]:
        """Get set of changed files between refs."""
        diff = self.repo.git.diff("--name-only", f"{since}..{upto}")
        return set(line.strip() for line in diff.splitlines() if line.strip())

    def get_change_stats(self, since: str, upto: str, file_path: str) -> Tuple[int, int]:
        """Get (insertions, deletions) for file between refs."""
        numstat = self.repo.git.diff("--numstat", f"{since}..{upto}", "--", file_path)
        lines = numstat.splitlines()
        if not lines:
            return 0, 0
        parts = lines[0].split("\t")
        if len(parts) < 3:
            return 0, 0
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            return 0, 0

    def get_historical_merge_touches(self, file_path: str) -> int:
        """Count merge commits that touched the file (proxy for conflict risk)."""
        log_output = self.repo.git.log(
            "--merges",
            "--follow",
            file_path,
            "--format=format:%H",
        )
        return len([line for line in log_output.splitlines() if line.strip()])
