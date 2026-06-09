import re
from typing import Iterator
from .models import GCEvent

def parse_gc_log(lines: Iterator[str]) -> list[GCEvent]:
    events = []
    pattern = re.compile(r'gen (?P<gen>\d+) .*?collected (?P<collected>\d+).*?uncollectable (?P<uncoll>\d+).*?took (?P<dur>[\d.]+)ms')
    for line in lines:
        if m := pattern.search(line):
            events.append(GCEvent(int(m['gen']), int(m['collected']), int(m['uncoll']), float(m['dur']), 0.0))
    return events