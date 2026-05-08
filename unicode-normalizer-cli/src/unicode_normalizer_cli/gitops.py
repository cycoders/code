from pathlib import Path
import git


class GitOps:
    """Git operations wrapper."""

    def __init__(self, root: Path):
        self.repo = git.Repo(root)

    def mv(self, old: Path, new: Path):
        """Git mv (stages rename)."""
        self.repo.git.mv(str(old), str(new))

    def add(self, paths: list[str]):
        """Stage paths."""
        self.repo.index.add(paths)

    def commit(self, message: str):
        """Commit staged changes."""
        if self.repo.index.diff(None):
            self.repo.index.commit(message)
        else:
            print("No changes to commit.")