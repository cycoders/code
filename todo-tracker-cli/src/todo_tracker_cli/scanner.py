import fnmatch
import re
from pathlib import Path
from typing import Iterator, Dict, List, Optional

from .models import TodoItem


LANG_PATTERNS: Dict[str, str] = {
    '.py': r'#\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.sh': r'#\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.js': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.ts': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.jsx': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.tsx': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.go': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.rs': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.java': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.c': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.cpp': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
    '.h': r'//\s*(TODO|FIXME|HACK)\s*[:\-]?\s*(.*)',
}


def get_pattern(suffix: str, tags: List[str]) -> Optional[str]:
    """Get regex pattern for language suffix and tags."""
    base = LANG_PATTERNS.get(suffix)
    if base:
        tag_pattern = '|'.join(re.escape(t) for t in tags)
        return re.sub(r'(TODO|FIXME|HACK)', tag_pattern, base)
    return None


def is_ignored(path: Path, ignore_globs: List[str]) -> bool:
    """Check if path matches any glob."""
    return any(fnmatch.fnmatch(str(path), glob) for glob in ignore_globs)


def scan(
    root: Path,
    ignore_globs: List[str],
    tags: List[str] = None,
) -> Iterator[TodoItem]:
    """Scan directory tree for todo comments."""
    tags = tags or ['TODO', 'FIXME', 'HACK']
    default_ignores = [
        '.git/**',
        'venv/**',
        'env/**',
        'node_modules/**',
        '__pycache__/**',
        'dist/**',
        'build/**',
        '*.egg-info/**',
    ]
    ignore_globs = default_ignores + ignore_globs

    for path in root.rglob('*'):
        if path.is_file() and not is_ignored(path, ignore_globs):
            pattern = get_pattern(path.suffix.lower(), tags)
            if pattern:
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_no, line in enumerate(f, 1):
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                tag = match.group(1).strip().upper()
                                msg = match.group(2).strip()
                                if msg:
                                    rel_path = path.relative_to(root).as_posix()
                                    yield TodoItem(rel_path, line_no, tag, msg)
                except (OSError, UnicodeError):
                    pass  # Skip unreadable files