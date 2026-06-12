import time
import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class Lease:
    key: str
    token: str
    expires_at: float
    _released: bool = False

    def release(self) -> None:
        if self._released:
            raise RuntimeError("lease already released")
        self._released = True

class LeaseClient:
    def __init__(self, backend: str = "memory") -> None:
        self.backend = backend
        self._leases: dict[str, Lease] = {}

    def acquire(self, key: str, ttl: int = 30) -> Lease:
        token = uuid.uuid4().hex
        lease = Lease(key=key, token=token, expires_at=time.monotonic() + ttl)
        self._leases[key] = lease
        return lease

    def validate(self, lease: Lease) -> bool:
        return (not lease._released and
                time.monotonic() < lease.expires_at)