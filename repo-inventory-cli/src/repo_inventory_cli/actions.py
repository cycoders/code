import subprocess
from pathlib import Path
from typing import Optional

from git import Repo


def open_repo(abs_path: str, editor: str = "code") -> None:
    try:
        subprocess.run([editor, abs_path], check=True)
    except FileNotFoundError:
        print(f"Editor '{editor}' not found. Install it or use 'code', 'vim', etc.")
    except subprocess.CalledProcessError:
        print(f"Failed to open {abs_path}")


def gc_repo(abs_path: str, aggressive: bool = False) -> None:
    try:
        repo = Repo(abs_path)
        opts = ["--aggressive"] if aggressive else []
        repo.git.gc(*opts)
        print(f"GC complete (aggressive: {aggressive})")
    except Exception as e:
        print(f"GC failed: {e}")
