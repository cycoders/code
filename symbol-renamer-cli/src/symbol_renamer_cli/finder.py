from __future__ import annotations
from pathlib import Path
from typing import List

from rich.console import Console


def get_py_files(paths: List[Path], console: Console) -> List[Path]:
    """Find all .py files recursively, skipping common ignores."""
    files: List[Path] = []
    ignore_dirs = {
        ".git",
        "venv",
        "env",
        ".venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        "dist",
        "build",
        ".tox",
        "htmlcov",
    }

    for path in paths:
        if not path.exists():
            console.print(f"[red]{path} does not exist[/]", err=True)
            continue

        if path.is_file():
            if path.suffix.lower() == ".py" and should_process(path, ignore_dirs):
                files.append(path)
        elif path.is_dir():
            for py_file in path.rglob("*.py"):
                if should_process(py_file, ignore_dirs):
                    files.append(py_file)

    return files


def should_process(file_path: Path, ignore_dirs: set[str]) -> bool:
    """Check if file should be processed (skip ignores)."""
    try:
        rel_parts = file_path.resolve().relative_to(file_path.anchor).parts
    except ValueError:
        return False

    for part in rel_parts:
        if part in ignore_dirs or part.startswith("."):
            return False
    return True