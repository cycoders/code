from typing import List, Tuple, Dict, Any

from .policies import BaseCache

class CacheSimulator:
    def __init__(self, policy_cls: type[BaseCache], capacity: int):
        self.policy_cls = policy_cls
        self.capacity = capacity
        self.reset()

    def reset(self):
        self.policy = self.policy_cls(self.capacity)
        self.hits: int = 0
        self.accesses: int = 0
        self.total_bytes: int = 0
        self.byte_hits: int = 0
        self.max_size: int = 0

    def simulate(self, accesses: List[Tuple[str, int]]) -> Dict[str, Any]:
        self.reset()
        for key, size in accesses:
            self.accesses += 1
            self.total_bytes += size
            if self.policy.has(key):
                self.hits += 1
                self.byte_hits += size
                self.policy.hit(key)
            else:
                self.policy.miss(key, size)
            self.max_size = max(self.max_size, self.policy.current_size)

        return {
            "hit_rate": self.hits / self.accesses,
            "byte_hit_rate": self.byte_hits / self.total_bytes if self.total_bytes else 0,
            "evictions": self.policy.evictions,
            "max_size": self.max_size,
            "final_size": self.policy.current_size,
            "accesses": self.accesses,
            **self.policy.get_stats(),
        }