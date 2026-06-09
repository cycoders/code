from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

BIDI_CHARS = {
    "\u202a": "LRE", "\u202b": "RLE", "\u202c": "PDF",
    "\u202d": "LRO", "\u202e": "RLO",
    "\u2066": "LRI", "\u2067": "RLI", "\u2068": "FSI",
    "\u2069": "PDI",
}

@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    column: int
    char: str
    name: str
    risk: str


def scan_file(path: Path) -> Iterator[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for lineno, line in enumerate(text.splitlines(), 1):
        for col, ch in enumerate(line, 1):
            if ch in BIDI_CHARS:
                name = BIDI_CHARS[ch]
                risk = "high" if name in ("RLO", "LRO", "RLI") else "medium"
                yield Finding(path, lineno, col, ch, name, risk)