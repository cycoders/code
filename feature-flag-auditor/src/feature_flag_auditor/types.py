from typing import NamedTuple

from pathlib import Path


class Usage(NamedTuple):
    file: Path
    line: int
    flag: str
    snippet: str
