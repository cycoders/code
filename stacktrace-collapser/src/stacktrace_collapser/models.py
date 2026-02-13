from typing import Optional
from pydantic import BaseModel


class Frame(BaseModel):
    """A single stack frame."""

    file: str
    line: int
    func: str
    col: Optional[int] = None
    count: int = 1


class Stacktrace(BaseModel):
    """Parsed and collapsed stacktrace."""

    language: str
    frames: list[Frame]
    error: Optional[str] = None  # TODO: extract from content
