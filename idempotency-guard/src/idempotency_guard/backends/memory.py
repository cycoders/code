import time
from typing import Any, Optional
from .base import BaseBackend

class MemoryBackend(BaseBackend):
    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Optional[dict[str, Any]]:
        entry = self._store.get(key)
        if entry and time.time() > entry.get("expires_at", 0):
            del self._store[key]
            return None
        return entry["value"] if entry else None

    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        self._store[key] = {"value": value, "expires_at": time.time() + ttl}

    def delete(self, key: str) -> None:
        self._store.pop(key, None)