import difflib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

from .cli import console, PRETTIER_EXTS
from .file_utils import SUPPORTED_EXTS


def get_formatter(file_path: Path) -> Optional[str]:
    ext = file_path.suffix.lower()
    if ext in {".py", ".pyi"}:
        return "ruff"
    elif ext in PRETTIER_EXTS:
        return "prettier"
    return None


def get_preview_diff(file_path: Path) -> Optional[str]:
    """
    Return unified diff str if changes needed, else None.
    """
    if not file_path.is_file():
        return None

    formatter = get_formatter(file_path)
    if not formatter:
        return None

    original_content = file_path.read_text(errors="ignore")

    tmp_path = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=file_path.suffix)
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmpf:
            tmpf.write(original_content)

        apply_formatter(tmp_path, formatter)

        formatted_content = Path(tmp_path).read_text(errors="ignore")

        if formatted_content == original_content:
            return None

        diff_lines = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            formatted_content.splitlines(keepends=True),
            fromfile=str(file_path),
            tofile=str(file_path) + " (fixed)",
            lineterm="",
            n=3,
        )
        return "".join(diff_lines)

    except FileNotFoundError as e:
        tool = "ruff" if formatter == "ruff" else "prettier"
        console.print(
            f"[red]✗ {tool.title()} not found: pipx install ruff / npm i -g prettier[/red]"
        )
        return None
    except subprocess.CalledProcessError as e:
        console.print(f"[yellow]✗ Formatter failed on {file_path.name}: {e}[/yellow]")
        return None
    except UnicodeError:
        console.print(f"[yellow]✗ Skipped binary/non-UTF8: {file_path.name}[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]✗ Error {file_path.name}: {str(e)[:100]}[/red]")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def apply_formatter(tmp_path: str, formatter: str) -> None:
    """Apply formatter to tmp file."""
    if formatter == "ruff":
        subprocess.run(["ruff", "format", tmp_path], check=True, capture_output=True)
        # Lint fixes (non-fatal)
        subprocess.run(
            ["ruff", "check", "--fix", "--quiet", tmp_path],
            capture_output=True,
        )
    elif formatter == "prettier":
        subprocess.run(["prettier", "--write", tmp_path], check=True, capture_output=True)


def apply_formatter_from_diff(file_path: Path) -> None:
    """Apply changes to original file (backup via git)."""
    formatter = get_formatter(file_path)
    if not formatter:
        raise ValueError("Unsupported file")

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=file_path.suffix)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(file_path.read_text())
        apply_formatter(tmp_path, formatter)
        shutil.copy2(tmp_path, str(file_path))
    finally:
        os.unlink(tmp_path)
