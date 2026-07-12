from __future__ import annotations

import dataclasses
import re
from typing import Iterable, List, Optional

@dataclasses.dataclass(frozen=True, order=True)
class MediaRange:
    type: str
    subtype: str
    params: tuple[tuple[str, str], ...] = dataclasses.field(default_factory=tuple)
    q: float = 1.0

    def matches(self, offered: str) -> bool:
        otype, osub = offered.split("/", 1)
        return (self.type in ("*", otype) and self.subtype in ("*", osub))

class Resolution:
    def __init__(self, media_range: MediaRange, offered: str, score: float):
        self.media_range = media_range
        self.offered = offered
        self.score = score

def _parse(header: str) -> List[MediaRange]:
    ranges: List[MediaRange] = []
    for part in header.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"([\w*]+)/([\w*+-]+)([^;]*)(?:;q=([0-9.]+))?", part)
        if not m:
            continue
        typ, sub, params, q = m.groups()
        qval = float(q) if q else 1.0
        ranges.append(MediaRange(typ.lower(), sub.lower(), tuple(), qval))
    return sorted(ranges, key=lambda r: (-r.q, r.type != "*", r.subtype != "*"))

def resolve(accept: str, offered: Iterable[str]) -> Optional[Resolution]:
    """Return best matching offered type or None."""
    parsed = _parse(accept)
    for offered_type in offered:
        for mr in parsed:
            if mr.matches(offered_type):
                return Resolution(mr, offered_type, mr.q)
    return None