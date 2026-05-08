from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


class GitIgnoreMatcher:
    """Matcher for gitignore patterns."""

    def __init__(self, root: Path):
        self.root = root
        self.spec: PathSpec = self._load_patterns()

    def _load_patterns(self) -> PathSpec:
        patterns = []
        for gitignore_path in [self.root / ".gitignore", self.root / ".git" / "info" / "exclude"]:
            if gitignore_path.exists():
                try:
                    with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                        patterns.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
                except OSError:
                    pass
        return PathSpec.from_lines(GitWildMatchPattern, patterns)

    def __call__(self, relpath: Path) -> bool:
        """Return True if should skip (matched ignore)."""
        return self.spec.match_file(relpath.relative_to(self.root).as_posix())


def walk_files(root: Path):
    """Walk files, skipping gitignored."""
    matcher = GitIgnoreMatcher(root)
    for path in root.rglob("*"):
        if path.is_file() and not matcher(path):
            yield path