from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Any
from time import perf_counter


@dataclass
class Decision:
    allowed: bool
    remaining: Optional[int] = None


class RateLimiter(ABC):
    """Abstract base for rate limiters."""

    @abstractmethod
    def is_allowed(self, key: str, now: float) -> Decision:
        """Check if request for key is allowed at time now."""
        ...

    def clear(self) -> None:
        """Clear all state."""
        pass


class FixedWindow(RateLimiter):
    """Fixed window counter. Resets count at window boundaries."""

    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._starts: Dict[str, float] = {}
        self._counts: Dict[str, int] = {}

    def is_allowed(self, key: str, now: float) -> Decision:
        if key not in self._starts or now - self._starts[key] > self.window:
            self._starts[key] = now
            self._counts[key] = 0
        if self._counts[key] >= self.limit:
            return Decision(False)
        self._counts[key] += 1
        return Decision(True, self.limit - self._counts[key])


class SlidingWindow(RateLimiter):
    """Sliding window list. Prunes old requests. O(n) worst, fine for sim."""

    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._requests: Dict[str, list[float]] = {}

    def is_allowed(self, key: str, now: float) -> Decision:
        if key not in self._requests:
            self._requests[key] = []
        reqs = self._requests[key]
        # Prune expired
        reqs[:] = [t for t in reqs if now - t < self.window]
        if len(reqs) >= self.limit:
            return Decision(False)
        reqs.append(now)
        return Decision(True, self.limit - len(reqs))


@dataclass
class BucketState:
    tokens: float
    last_refill: float


class TokenBucket(RateLimiter):
    """Token bucket with continuous refill."""

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._states: Dict[str, BucketState] = {}

    def _get_state(self, key: str, now: float) -> BucketState:
        if key not in self._states:
            state = BucketState(self.capacity, now)
            self._states[key] = state
            return state
        state = self._states[key]
        delta = now - state.last_refill
        state.tokens = min(self.capacity, state.tokens + delta * self.refill_rate)
        state.last_refill = now
        return state

    def is_allowed(self, key: str, now: float) -> Decision:
        state = self._get_state(key, now)
        if state.tokens < 1.0:
            return Decision(False, 0)
        state.tokens -= 1.0
        return Decision(True, int(state.tokens))


class LeakyBucket(RateLimiter):
    """Leaky bucket. Leaks continuously, enqueues if space."""

    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self._queues: Dict[str, tuple[float, float]] = {}

    def _leak(self, key: str, now: float) -> float:
        if key not in self._queues:
            self._queues[key] = (now, 0.0)
            return 0.0
        last_time, size = self._queues[key]
        delta = now - last_time
        leaked = min(size, delta * self.leak_rate)
        size -= leaked
        self._queues[key] = (now, size)
        return size

    def is_allowed(self, key: str, now: float) -> Decision:
        size = self._leak(key, now)
        if size >= self.capacity:
            return Decision(False)
        new_size = size + 1
        last_time = self._queues[key][0]
        self._queues[key] = (last_time, new_size)
        return Decision(True, self.capacity - int(new_size))


def create_policy(name: str, params: dict[str, Any]) -> RateLimiter:
    """Factory for policies."""
    name = name.lower()
    if name == "fixed":
        return FixedWindow(params["limit"], params["window"])
    if name == "sliding":
        return SlidingWindow(params["limit"], params["window"])
    if name == "token":
        return TokenBucket(params["capacity"], params["refill_rate"])
    if name == "leaky":
        return LeakyBucket(params["capacity"], params["leak_rate"])
    raise ValueError(f"Unknown policy: {name}")