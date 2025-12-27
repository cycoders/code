from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class Message:
    """Extracted translatable message."""
    singular: str
    plural: Optional[str] = None
    location: Tuple[str, int] = ("unknown", 0)  # file, lineno

    def __repr__(self) -> str:
        return f"Message(singular='{self.singular}', plural={self.plural})"