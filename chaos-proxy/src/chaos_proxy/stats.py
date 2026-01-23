import asyncio
import time
from typing import Self


class Stats:
    def __init__(self: Self) -> None:
        self._lock = asyncio.Lock()
        self.start_time = time.monotonic()
        self.req_bytes: int = 0
        self.resp_bytes: int = 0
        self.drops_req: int = 0
        self.drops_resp: int = 0
        self.conn_active: int = 0

    async def record_bytes(self: Self, direction: str, count: int) -> None:
        async with self._lock:
            if direction == "req":
                self.req_bytes += count
            else:
                self.resp_bytes += count

    def record_drop(self: Self, direction: str) -> None:
        # Sync for speed, low contention
        if direction == "req":
            self.drops_req += 1
        else:
            self.drops_resp += 1

    @property
    def total_drops(self: Self) -> int:
        return self.drops_req + self.drops_resp

    @property
    def loss_pct(self: Self) -> float:
        total = self.req_bytes + self.resp_bytes
        return self.total_drops / total if total else 0.0

    @property
    def avg_latency_req(self: Self) -> float:
        # Placeholder: extend with measured delays if needed
        return 0.0

    @property
    def avg_latency_resp(self: Self) -> float:
        return 0.0
