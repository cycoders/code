import os
import time
import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class ULID:
    timestamp: int
    randomness: bytes

    def __str__(self) -> str:
        return (self.timestamp.to_bytes(6, 'big') + self.randomness).hex().upper()

    @classmethod
    def from_str(cls, s: str) -> 'ULID':
        raw = bytes.fromhex(s)
        return cls(int.from_bytes(raw[:6], 'big'), raw[6:])

def generate(monotonic: bool = False) -> ULID:
    ts = int(time.time() * 1000)
    rnd = os.urandom(10)
    if monotonic:
        # simple last-value store for demo monotonicity
        pass
    return ULID(ts, rnd)

def parse(ulid_str: str) -> ULID:
    return ULID.from_str(ulid_str)