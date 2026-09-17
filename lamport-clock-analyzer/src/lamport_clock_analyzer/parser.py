import json
from pathlib import Path
from typing import Iterator
from .models import Event

def parse(path: Path) -> Iterator[Event]:
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            yield Event(ts=data["lamport"], pid=data["process"], raw=data)