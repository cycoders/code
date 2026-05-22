import hashlib
from typing import Dict, List

class ConsistentHashRing:
    def __init__(self, nodes: List[str], vnodes: int = 128):
        self.vnodes = vnodes
        self.ring: Dict[int, str] = {}
        self.nodes = set()
        for node in nodes:
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_node(self, node: str):
        self.nodes.add(node)
        for i in range(self.vnodes):
            h = self._hash(f"{node}:{i}")
            self.ring[h] = node

    def remove_node(self, node: str):
        self.nodes.discard(node)
        self.ring = {h: n for h, n in self.ring.items() if n != node}

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise ValueError("Ring is empty")
        h = self._hash(key)
        for pos in sorted(self.ring.keys()):
            if pos >= h:
                return self.ring[pos]
        return self.ring[min(self.ring.keys())]