from __future__ import annotations
import re
from pathlib import Path
from typing import Iterator

from .categories import INVISIBLE_CATEGORIES

Pattern = re.compile("|".join(INVISIBLE_CATEGORIES.values()))


def scan_file(path: Path) -> Iterator[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for match in Pattern.finditer(text):
        yield {
            "file": str(path),
            "offset": match.start(),
            "char": match.group(),
            "category": next(k for k, v in INVISIBLE_CATEGORIES.items() if re.match(v, match.group())),
        }
