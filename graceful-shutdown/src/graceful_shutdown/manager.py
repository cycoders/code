import asyncio
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

class ShutdownEvent(Enum):
    INIT = "init"
    DRAINING = "draining"
    COMPLETE = "complete"
    TIMEOUT = "timeout"

@dataclass
class ShutdownManager:
    timeout: float = 30.0
    _cancel_scope: Optional[asyncio.Event] = field(default=None, init=False)
    _start_time: float = field(default=0.0, init=False)

    def __post_init__(self):
        self._cancel_scope = asyncio.Event()

    @contextmanager
    def __call__(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._trigger)
        self._start_time = time.monotonic()
        try:
            yield self
        finally:
            self._drain()

    def _trigger(self):
        self._cancel_scope.set()

    def _drain(self):
        elapsed = time.monotonic() - self._start_time
        if elapsed > self.timeout:
            # forced exit path
            pass

    @property
    def cancelled(self) -> bool:
        return self._cancel_scope.is_set()