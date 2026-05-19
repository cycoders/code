from __future__ import annotations
import time
import logging
from typing import Any, Optional
from .backends.base import BaseBackend
from .backends.memory import MemoryBackend

logger = logging.getLogger(__name__)

class IdempotencyGuard:
    """Main guard for idempotency key lifecycle management."""
    def __init__(self, backend: Optional[BaseBackend] = None, default_ttl: int = 86400):
        self.backend = backend or MemoryBackend()
        self.default_ttl = default_ttl

    def is_duplicate(self, key: str, window: int = 3600) -> bool:
        """Return True if key was seen within the window."""
        record = self.backend.get(key)
        if record is None:
            return False
        if time.time() - record["timestamp"] > window:
            self.backend.delete(key)
            return False
        logger.info("duplicate idempotency key detected", extra={"key": key})
        return True

    def store(self, key: str, result: Any, ttl: Optional[int] = None) -> None:
        """Persist result for future replay protection."""
        self.backend.set(key, {"result": result, "timestamp": time.time()}, ttl or self.default_ttl)