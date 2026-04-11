"""Load and manage Unicode character data."""

import unicodedata
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

from .models import UnicodeChar


class DataLoader:
    """Handles loading all Unicode chars."""

    def __init__(self) -> None:
        self.chars: List[UnicodeChar] = []
        self.blocks: Dict[str, List[UnicodeChar]] = defaultdict(list)

    def load(self) -> None:
        """Load all named Unicode chars (runtime gen)."""
        print("Loading Unicode data...", file=sys.stderr)
        for cp in range(0x110000):
            try:
                char = UnicodeChar.from_codepoint(cp)
                self.chars.append(char)
                self.blocks[char.block].append(char)
            except ValueError:
                continue
        print(f"Loaded {len(self.chars):,} chars", file=sys.stderr)

    def get_sorted_blocks(self) -> List[str]:
        """Get sorted unique blocks."""
        return sorted(self.blocks.keys())


loader = DataLoader()
