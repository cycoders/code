from pathlib import Path
from typing import Iterator
import fnmatch


def find_python_files(root_path: str, ignores: list[str]) -> Iterator[Path]:
    """
    Yield all .py files under root_path, skipping ignored paths via fnmatch.

    >>> list(find_python_files('.', []))
    [PosixPath('src/deadcode_hunter/finder.py'), ...]
    """
    root = Path(root_path).resolve()
    for path in root.rglob("*.py"):
        rel_path = path.relative_to(root)
        rel_str = str(rel_path)  # or rel_path.as_posix()
        if not any(fnmatch.fnmatch(rel_str, pattern) for pattern in ignores):
            yield path
