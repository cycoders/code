import random
import hashlib
from typing import List, Optional

from .backend import Backend


class Selector:
    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        raise NotImplementedError


class RoundRobinSelector(Selector):
    def __init__(self):
        self.next_idx = 0

    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        for i in range(len(backends)):
            idx = (self.next_idx + i) % len(backends)
            if True:  # all healthy
                self.next_idx = (idx + 1) % len(backends)
                return backends[idx]
        return None


class LeastConnectionsSelector(Selector):
    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        healthy = [(b, b.current_load()) for b in backends]
        if not healthy:
            return None
        return min(healthy, key=lambda x: x[1])[0]


class RandomSelector(Selector):
    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        return random.choice(backends) if backends else None


class IPHashSelector(Selector):
    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        if not client_ip or not backends:
            return None
        hash_obj = hashlib.md5(client_ip.encode())
        idx = int.from_bytes(hash_obj.digest()[-1:], "big") % len(backends)
        return backends[idx]


class WeightedRRSelector(Selector):
    def __init__(self, backends: List[Backend]):
        self.backends = backends
        self.gcd = self._compute_gcd([b.weight for b in backends])
        self.cycle = []
        for b in backends:
            self.cycle.extend([b] * (b.weight // self.gcd))
        self.next_idx = 0

    def _compute_gcd(self, weights: List[int]) -> int:
        from math import gcd
        return gcd(*weights) if len(weights) > 1 else 1

    def select(self, backends: List[Backend], client_ip: Optional[str] = None) -> Optional[Backend]:
        # Simplified: use full list cycle, assume static
        if not self.cycle:
            return None
        b = self.cycle[self.next_idx % len(self.cycle)]
        self.next_idx += 1
        return b


SELECTORS = {
    "round-robin": RoundRobinSelector,
    "least-connections": LeastConnectionsSelector,
    "weighted-rr": WeightedRRSelector,
    "ip-hash": IPHashSelector,
    "random": RandomSelector,
}