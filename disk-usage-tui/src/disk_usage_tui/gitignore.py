from pathlib import Path
from pathspec import GitIgnoreSpec


def load_gitignore(root: Path) -> GitIgnoreSpec:
    """Load .gitignore from root as GitIgnoreSpec."""
    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file():
        return GitIgnoreSpec([])

    try:
        with gitignore_path.open("r", encoding="utf-8") as f:
            return GitIgnoreSpec.from_lines("", f.readlines())
    except Exception:
        return GitIgnoreSpec([])