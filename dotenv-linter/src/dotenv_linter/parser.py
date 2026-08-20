from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

@dataclass
class Entry:
    key: str
    value: str
    line: int
    raw: str

def parse_env(path: Path) -> list[Entry]:
    entries: list[Entry] = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        entries.append(Entry(key.strip(), value.strip(), i, line))
    return entries