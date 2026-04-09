import random
from abc import ABC, abstractmethod
from collections import OrderedDict, deque, defaultdict
from typing import Dict, Set, Any


class BaseCache(ABC):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.current_size = 0
        self._items: Dict[str, int] = {}  # key -> size
        self.evictions = 0

    def has(self, key: str) -> bool:
        return key in self._items

    def hit(self, key: str) -> None:
        pass

    def miss(self, key: str, size: int) -> None:
        self._make_space(size)
        self._items[key] = size
        self.current_size += size

    def _make_space(self, needed: int) -> None:
        while self.current_size + needed > self.capacity and self._items:
            victim = self._choose_victim()
            victim_size = self._items.pop(victim)
            self.current_size -= victim_size
            self.evictions += 1

    @abstractmethod
    def _choose_victim(self) -> str:
        pass

    def get_stats(self) -> Dict[str, Any]:
        return {
            "final_items": len(self._items),
        }


class LRUCache(BaseCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.order: OrderedDict[str, None] = OrderedDict()

    def hit(self, key: str) -> None:
        self.order.move_to_end(key)

    def miss(self, key: str, size: int) -> None:
        super().miss(key, size)
        self.order[key] = None

    def _choose_victim(self) -> str:
        return self.order.popitem(last=False)[0]


class FIFOCache(BaseCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.order: deque[str] = deque()

    def miss(self, key: str, size: int) -> None:
        super().miss(key, size)
        self.order.append(key)

    def _choose_victim(self) -> str:
        return self.order.popleft()


class LFUCache(BaseCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.key_to_freq: Dict[str, int] = {}
        self.freq_to_keys: Dict[int, Set[str]] = {}
        self.min_freq = 0

    def hit(self, key: str) -> None:
        old_freq = self.key_to_freq[key]
        self.freq_to_keys[old_freq].discard(key)
        if not self.freq_to_keys[old_freq]:
            del self.freq_to_keys[old_freq]
            if old_freq == self.min_freq and self.freq_to_keys:
                self.min_freq = min(self.freq_to_keys)

        new_freq = old_freq + 1
        self.key_to_freq[key] = new_freq
        self.freq_to_keys.setdefault(new_freq, set()).add(key)
        self.min_freq = min(self.min_freq, new_freq)

    def miss(self, key: str, size: int) -> None:
        self.key_to_freq[key] = 1
        self.freq_to_keys.setdefault(1, set()).add(key)
        if self.min_freq == 0:
            self.min_freq = 1
        super().miss(key, size)

    def _choose_victim(self) -> str:
        while True:
            if self.min_freq not in self.freq_to_keys or not self.freq_to_keys[self.min_freq]:
                if self.freq_to_keys:
                    self.min_freq = min(self.freq_to_keys)
                else:
                    raise RuntimeError("Cache empty, cannot evict")
                continue
            key = self.freq_to_keys[self.min_freq].pop()
            if not self.freq_to_keys[self.min_freq]:
                del self.freq_to_keys[self.min_freq]
            del self.key_to_freq[key]
            return key


class RandomCache(BaseCache):
    def _choose_victim(self) -> str:
        if not self._items:
            raise RuntimeError("Cache empty")
        return random.choice(list(self._items))
