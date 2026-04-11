"""Data models for Unicode characters."""

import unicodedata
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UnicodeChar:
    """Immutable model for a Unicode character."""

    codepoint: str
    char: str
    name: str
    category: str
    block: str
    bidirectional: str
    mirrored: str
    decomposition: str
    east_asian_width: str

    @classmethod
    def from_codepoint(cls, cp: int) -> "UnicodeChar":
        """Create from codepoint int."""
        c = chr(cp)
        try:
            name = unicodedata.name(c)
        except ValueError as e:
            raise ValueError(f"No name for U+{cp:04X}") from e
        return cls(
            codepoint=f"U+{cp:04X}",
            char=c,
            name=name,
            category=unicodedata.category(c),
            block=unicodedata.block(c),
            bidirectional=unicodedata.bidirectional(c),
            mirrored=str(unicodedata.mirrored(c)),
            decomposition=unicodedata.decomposition(c),
            east_asian_width=unicodedata.east_asian_width(c),
        )

    def to_dict(self) -> dict[str, Any]:
        """JSON serializable dict."""
        return {k: v for k, v in self.__dict__.items()}
