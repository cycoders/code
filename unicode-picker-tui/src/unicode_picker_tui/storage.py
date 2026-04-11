"""Favorites storage management."""

import json
from pathlib import Path
from typing import Set


class Favorites:
    """Persist favorites codepoints."""

    def __init__(self, storage_path: Path) -> None:
        self.path = storage_path / "favs.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._favs: Set[str] = set()
        self.load()

    def load(self) -> None:
        """Load from JSON."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                self._favs = set(data)
            except (json.JSONDecodeError, KeyError):
                self._favs = set()

    def save(self) -> None:
        """Save to JSON."""
        with open(self.path, "w") as f:
            json.dump(sorted(self._favs), f)

    def toggle(self, codepoint: str) -> bool:
        """Toggle and save. Returns is_fav now."""
        if codepoint in self._favs:
            self._favs.discard(codepoint)
        else:
            self._favs.add(codepoint)
        self.save()
        return codepoint in self._favs

    def is_fav(self, codepoint: str) -> bool:
        return codepoint in self._favs

    @property
    def count(self) -> int:
        return len(self._favs)
