'''Diff computation and printing.''' 

import difflib
import os
import subprocess
import tempfile
from pathlib import Path
from rich.console import Console

from .normalizer import normalize_content

console = Console()

def print_semantic_diff(filepath: str, content_old: str, content_new: str) -> None:
    """Print semantic diff for a file, using git for colors if possible."""
    norm_old = normalize_content(filepath, content_old)
    norm_new = normalize_content(filepath, content_new)

    if norm_old == norm_new:
        console.print(f"[green]No semantic changes: {filepath}[/]")
        return

    # Use git diff --no-index for beautiful colored output
    with tempfile.NamedTemporaryFile(mode='w', suffix=Path(filepath).suffix, delete=False, encoding='utf-8') as f_old, \
         tempfile.NamedTemporaryFile(mode='w', suffix=Path(filepath).suffix, delete=False, encoding='utf-8') as f_new:
        f_old.write(norm_old)
        f_old.flush()
        f_new.write(norm_new)
        f_new.flush()
        temp_old, temp_new = f_old.name, f_new.name

    try:
        proc = subprocess.run(
            ['git', 'diff', '--no-index', '--color=always', temp_old, temp_new],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        console.print(proc.stdout, markup=False)  # Preserve ANSI
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[yellow]git diff unavailable, using plain diff[/]")
        lines_old = norm_old.splitlines(keepends=True)
        lines_new = norm_new.splitlines(keepends=True)
        plain_diff = ''.join(difflib.unified_diff(lines_old, lines_new, fromfile=filepath, tofile=filepath))
        console.print(plain_diff, style="dim")
    finally:
        for temp_file in (temp_old, temp_new):
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    console.print("")  # Spacer
