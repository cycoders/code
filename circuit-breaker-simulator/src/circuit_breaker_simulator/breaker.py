from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Deque
import time
import random
from .models import BreakerConfig

class BreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass(frozen=True)
class Breaker:
    """Base circuit breaker interface. Implementations override allow/on_result."""

    name: str
    config: BreakerConfig
    state: BreakerState = BreakerState.CLOSED
    last_failure_time: float = 0.0
    consecutive_failures: int = 0
    failure_times: Deque[float] = None  # for threshold

    @property
    @abstractmethod
    def allow(self) -> bool:
        pass

    @abstractmethod
    def on_result(self, success: bool):
        pass


class ConsecutiveBreaker(Breaker):
    def __init__(self, name: str, config: BreakerConfig):
        super().__init__(name=name, config=config)
        self.consecutive_failures = 0

    @property
    def state(self) -> BreakerState:
        if self._is_open():
            return BreakerState.OPEN
        if self.consecutive_failures >= self.config.consec_threshold:
            return BreakerState.OPEN
        return BreakerState.CLOSED

    def allow(self) -> bool:
        return self.state != BreakerState.OPEN

    def on_result(self, success: bool):
        now = time.time()
        if success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.last_failure_time = now

    def _is_open(self) -> bool:
        return (time.time() - self.last_failure_time) < self.config.timeout_secs and self.consecutive_failures >= self.config.consec_threshold


class ThresholdBreaker(Breaker):
    def __init__(self, name: str, config: BreakerConfig):
        super().__init__(name=name, config=config)
        from collections import deque
        self.failure_times: Deque[float] = deque(maxlen=config.window_secs * 10)  # approx

    @property
    def state(self) -> BreakerState:
        if self._is_open():
            return BreakerState.OPEN
        recent_failures = sum(1 for ts in self.failure_times if time.time() - ts < self.config.window_secs)
        if recent_failures >= self.config.failure_threshold:
            return BreakerState.OPEN
        return BreakerState.CLOSED

    def allow(self) -> bool:
        return self.state != BreakerState.OPEN

    def on_result(self, success: bool):
        now = time.time()
        if not success:
            self.failure_times.append(now)
            self.last_failure_time = now

    def _is_open(self) -> bool:
        return (time.time() - self.last_failure_time) < self.config.timeout_secs


def create_breaker(name: str, config: BreakerConfig) -> Breaker:
    if config.type == "consecutive":
        return ConsecutiveBreaker(name, config)
    elif config.type == "threshold":
        return ThresholdBreaker(name, config)
    raise ValueError(f"Unknown breaker type: {config.type}")
