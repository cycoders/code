from .ring import ConsistentHashRing
from collections import Counter

class Simulator:
    def __init__(self, nodes: int = 5, vnodes: int = 128, keys: int = 10000):
        self.nodes = [f"node-{i}" for i in range(nodes)]
        self.ring = ConsistentHashRing(self.nodes, vnodes)
        self.keys = [f"key-{i}" for i in range(keys)]

    def run(self):
        placement = [self.ring.get_node(k) for k in self.keys]
        return Counter(placement)