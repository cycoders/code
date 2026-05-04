from abc import ABC, abstractmethod
import random


class BackoffStrategy(ABC):
    """Stateful backoff strategy base."""

    def __init__(self, base_delay: float, max_delay: float, factor: float):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.prev_delay = 0.0

    @abstractmethod
    def next_delay(self, attempt: int) -> float:
        pass


class FixedStrategy(BackoffStrategy):
    def next_delay(self, attempt: int) -> float:
        return self.base_delay


class ExponentialStrategy(BackoffStrategy):
    def next_delay(self, attempt: int) -> float:
        delay = self.base_delay * (self.factor ** (attempt - 1))
        return min(delay, self.max_delay)


class FullJitterStrategy(BackoffStrategy):
    def next_delay(self, attempt: int) -> float:
        cap = self.base_delay * (self.factor ** (attempt - 1))
        cap = min(cap, self.max_delay)
        return random.random() * cap


class EqualJitterStrategy(BackoffStrategy):
    def next_delay(self, attempt: int) -> float:
        cap = self.base_delay * (self.factor ** (attempt - 1))
        cap = min(cap, self.max_delay)
        lower = cap / 2
        return random.uniform(lower, cap)


class DecorrelatedJitterStrategy(BackoffStrategy):
    def next_delay(self, attempt: int) -> float:
        if self.prev_delay == 0:
            self.prev_delay = self.base_delay
        else:
            self.prev_delay = random.uniform(
                self.base_delay, min(self.max_delay, self.prev_delay * 3)
            )
        return self.prev_delay


STRATEGIES = {
    "fixed": FixedStrategy,
    "exponential": ExponentialStrategy,
    "full_jitter": FullJitterStrategy,
    "equal_jitter": EqualJitterStrategy,
    "decorrelated_jitter": DecorrelatedJitterStrategy,
}
