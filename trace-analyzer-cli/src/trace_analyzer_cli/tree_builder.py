from __future__ import annotations
from typing import List

from .models import Span


class SpanNode:
    """Tree node for spans with computed metrics."""

    __slots__ = ("span", "children", "self_time")

    def __init__(self, span: Span):
        self.span = span
        self.children: List[SpanNode] = []
        self.self_time: float = 0.0

    def flatten(self) -> list[SpanNode]:
        """Yield all descendant nodes depth-first."""
        yield self
        for child in self.children:
            yield from child.flatten()
