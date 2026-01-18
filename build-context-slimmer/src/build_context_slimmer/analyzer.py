from pathlib import Path
from typing import Dict, Set
from collections import defaultdict
import os


def get_all_file_sizes(context: Path) -> Dict[Path, int]:
    """Walk context, return {file: size}. Ignores symlinks/errors."""
    sizes: Dict[Path, int] = {}
    context = context.resolve()

    for root, _, files in os.walk(context):
        for file in files:
            try:
                p = Path(root) / file
                sizes[p.resolve()] = p.stat().st_size
            except (OSError, PermissionError):
                pass

    return sizes


def get_used_files(context: Path, patterns: list[str]) -> Set[Path]:
    """Compute files used by patterns (glob + dir recurse)."""
    used: Set[Path] = set()
    context = Path(context).resolve()

    for pattern in patterns:
        pattern_path = pattern
        if pattern_path.endswith("/"):
            # Dir copy: recurse contents
            dir_name = pattern_path.rstrip("/")
            dir_p = context / dir_name
            if dir_p.exists() and dir_p.is_dir():
                for p in dir_p.rglob("*"):
                    if p.is_file():
                        used.add(p.resolve())
        else:
            # Glob match
            for p in context.glob(pattern):
                if p.is_file():
                    used.add(p.resolve())
                elif p.is_dir():
                    # Matched dir: recurse
                    for pp in p.rglob("*"):
                        if pp.is_file():
                            used.add(pp.resolve())

    return used
