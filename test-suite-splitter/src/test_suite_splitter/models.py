from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class TestCase:
    """Immutable representation of a single test case with duration."""

    suite: str
    name: str
    duration: float

    @property
    def id(self) -> str:
        """Unique identifier: suite::name."""
        return f"{self.suite}::{self.name}"

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"TestCase(id='{self.id}', duration={self.duration:.3f}s)"