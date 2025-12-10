from dataclasses import dataclass
from typing import Optional


@dataclass
class Commit:
    """Parsed conventional commit."""

    sha: str
    type_: str
    scope: Optional[str]
    title: str
    breaking: bool = False