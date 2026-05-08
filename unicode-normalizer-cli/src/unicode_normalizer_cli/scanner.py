from pathlib import Path
from typing import Dict, Any, Optional

import unicodedata

from .walker import walk_files

_TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".txt", ".json",
    ".yaml", ".yml", ".html", ".htm", ".css", ".scss", ".xml",
    ".toml", ".ini", ".cfg", ".sh", ".bash", ".env", ".rst",
    ".tex", ".go", ".rs", ".java", ".kt", ".swift", ".php",
}


def is_text_file(path: Path, max_preview: int = 512) -> bool:
    """Heuristic to detect text files."""
    if path.suffix.lower() in _TEXT_SUFFIXES:
        return True
    try:
        raw = path.read_bytes()[:max_preview]
        if b"\x00" in raw:
            return False
        null_ratio = raw.count(b"\x00") / len(raw)
        if null_ratio > 0.01:
            return False
        return True
    except OSError:
        return False


def needs_normalization(s: str, form: str) -> tuple[bool, str]:
    """Check if string needs normalization. Returns (needs, normalized)."""
    try:
        normalized = unicodedata.normalize(form, s)
        return normalized != s, normalized
    except ValueError as e:
        raise ValueError(f"Invalid normalization form '{form}': {e}")


def scan_for_normalization(
    root: Path,
    form: str = "NFC",
    max_size: int = 10_485_760,
) -> Dict[Path, Dict[str, Any]]:
    """Scan for issues."""
    issues: Dict[Path, Dict[str, Any]] = {}
    for path in walk_files(root):
        stat = path.stat()
        if stat.st_size > max_size:
            continue
        if not is_text_file(path):
            continue
        try:
            content = path.read_text(errors="surrogateescape")
        except (UnicodeDecodeError, OSError):
            continue
        content_needs, norm_content = needs_normalization(content, form)
        name_needs, norm_name = needs_normalization(path.name, form)
        if content_needs or name_needs:
            issues[path] = {
                "content": content,
                "normalized_content": norm_content,
                "content_needs": content_needs,
                "name_needs": name_needs,
                "name": path.name,
                "normalized_name": norm_name,
                "type": "both" if content_needs and name_needs else "content" if content_needs else "name",
            }
    return issues