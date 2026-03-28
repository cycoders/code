from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Usage:
    """Represents a single environment variable usage in code."""

    file_path: Path
    line_num: int
    var_name: str
    snippet: str
    lang: str


UsageMap = dict[str, List[Usage]]
