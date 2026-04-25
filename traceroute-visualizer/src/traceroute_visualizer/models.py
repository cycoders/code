from dataclasses import dataclass
from typing import List

@dataclass
class Hop:
    hop_num: int
    ip: str
    rtts: List[float]  # ms, float('inf') for timeouts
    asn: str | None = None
    org: str | None = None
    country: str | None = None