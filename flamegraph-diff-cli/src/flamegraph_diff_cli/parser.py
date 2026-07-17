from pathlib import Path
from typing import Dict

def parse_folded(path: str) -> Dict[str, int]:
    """Parse Brendan Gregg folded stack format."""
    stacks: Dict[str, int] = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        stack, count = line.rsplit(' ', 1)
        stacks[stack] = stacks.get(stack, 0) + int(count)
    return stacks