from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CodeBlock:
    path: str
    start_line: int
    end_line: int
    token_str: str
    snippet: str


Dupe = Tuple[float, CodeBlock, CodeBlock]
