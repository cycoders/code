import shlex
from pathlib import Path
from typing import List

from .types import HistoryEntry
from datetime import datetime


def detect_format(path: Path) -> str:
    """Detect bash or zsh format from first few lines."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:5]
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(": "):
                return "zsh"
            if stripped.startswith("#") and stripped[1:].isdigit():
                return "bash"
        raise ValueError("Unable to detect format")
    except Exception:
        raise ValueError(f"Cannot detect format in {path}")


def parse_zsh_line(line: str) -> HistoryEntry | None:
    """Parse a single zsh history line."""
    stripped = line.strip()
    if not stripped.startswith(": "):
        return None
    try:
        parts = stripped.split(":", 2)
        if len(parts) < 3:
            return None
        ts_str = parts[1].strip()
        cmd_part = parts[2].strip()
        timestamp = datetime.fromtimestamp(float(ts_str)) if ts_str else None
        words = shlex.split(cmd_part)
        command = words[0] if words else cmd_part
        return HistoryEntry(timestamp, command, stripped, words)
    except (ValueError, IndexError):
        return None


def parse_bash_lines(lines: List[str]) -> List[HistoryEntry]:
    """Parse bash history lines (alternating #ts and cmd)."""
    entries = []
    i = 0
    while i < len(lines):
        ts_line = lines[i].strip()
        i += 1
        if i >= len(lines):
            break
        cmd_line = lines[i].strip()
        i += 1
        timestamp = None
        if ts_line.startswith("#") and ts_line[1:].isdigit():
            try:
                ts = int(ts_line[1:])
                timestamp = datetime.fromtimestamp(ts)
            except ValueError:
                pass
        words = shlex.split(cmd_line)
        command = words[0] if words else cmd_line
        entries.append(HistoryEntry(timestamp, command, cmd_line, words))
    return entries


def parse_history_file(path: Path, fmt: str | None = None) -> List[HistoryEntry]:
    """Parse history file."""
    if not path.exists():
        raise FileNotFoundError(f"History file not found: {path}")
    content = path.read_text(errors="ignore").splitlines()
    if fmt is None:
        fmt = detect_format(path)
    if fmt == "zsh":
        return [e for e in (parse_zsh_line(line) for line in content) if e]
    elif fmt == "bash":
        return parse_bash_lines(content)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
