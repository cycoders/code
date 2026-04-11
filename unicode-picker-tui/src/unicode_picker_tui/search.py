"""Fuzzy search over Unicode chars."""

from typing import List
from rapidfuzz import process, fuzz

from .models import UnicodeChar


def search_chars(chars: List[UnicodeChar], query: str, limit: int = 1000, threshold: int = 70) -> List[UnicodeChar]:
    """Fuzzy search chars by name."""
    if not query.strip():
        return chars
    matches = process.extract(
        chars,
        query,
        key=lambda c: c.name,
        scorer=fuzz.ratio,
        limit=limit,
    )
    return [match[0] for match in matches if match[1] >= threshold]
