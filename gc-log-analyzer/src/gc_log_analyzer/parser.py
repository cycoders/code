from dataclasses import dataclass
from typing import Iterator, List

@dataclass
class GCPause:
    timestamp: float
    duration_ms: float
    generation: str

def parse_gc_log(lines: Iterator[str]) -> List[GCPause]:
    pauses = []
    for line in lines:
        line = line.strip()
        if "[GC" in line and "ms" in line:
            # simplified unified logging parser
            parts = line.split()
            try:
                ts = float(parts[0].strip('['))
                dur = float([p for p in parts if p.endswith('ms')][0][:-2])
                gen = "old" if "Old" in line else "young"
                pauses.append(GCPause(ts, dur, gen))
            except (IndexError, ValueError):
                continue
    return pauses