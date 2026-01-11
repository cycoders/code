import asyncio
import math
from collections import deque
from typing import List, Optional, Tuple

from loguru import logger

from .config import Config
from .http_client import RateLimitClient
from .models import RateLimitInfo, TestStats


class RateLimitTester:
    """Core testing logic."""

    KNOWN_LIMIT_HEADERS = {
        "x-ratelimit-limit",
        "ratelimit-limit",
        "x-rate-limit-limit",
        "rate-limit-limit",
        "x-ratelimit-remaining",
        "ratelimit-remaining",
        "x-rate-limit-remaining",
        "rate-limit-remaining",
        "x-ratelimit-reset",
        "ratelimit-reset",
        "x-rate-limit-reset",
        "rate-limit-reset",
        "retry-after",
    }

    @classmethod
    def from_config(cls, config: Config) -> "RateLimitTester":
        return cls(config)

    def __init__(self, config: Config):
        self.config = config

    async def discover(self) -> RateLimitInfo:
        """Parse headers for limits."""
        logger.info(f"Discovering limits for {self.config.url}")
        async with RateLimitClient(self.config) as client:
            resp = await client.head(self.config.url)

        info = RateLimitInfo(headers_seen=[])
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}

        for h in self.KNOWN_LIMIT_HEADERS:
            if h in headers_lower:
                info.headers_seen.append(h)
                val = headers_lower[h]
                if "limit" in h:
                    info.limit = int(float(val))
                elif "remaining" in h:
                    info.remaining = int(float(val))
                elif "reset" in h:
                    info.reset_timestamp = int(float(val))
                elif h == "retry-after":
                    info.retry_after = float(val)

        if info.limit and info.reset_timestamp and info.remaining:
            info.window_seconds = math.ceil(info.reset_timestamp - (info.limit - info.remaining) / (info.limit / 60))  # Infer

        logger.debug(f"Parsed: {info.model_dump()}")
        return info

    async def _run_concurrent(self, n: int) -> Tuple[int, int]:
        """Run N concurrent requests, return (success, fail)."""
        sem = asyncio.Semaphore(self.config.concurrency)

        async def req():
            async with sem:
                async with RateLimitClient(self.config) as client:
                    resp = await client.get(self.config.url)
                    return resp.status_code < 400

        tasks = [req() for _ in range(n)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if r is True)
        return success, n - success

    async def measure_burst(self, max_conc: Optional[int] = None) -> int:
        """Binary search max burst."""
        low, high = 1, max_conc or 1000
        while low < high:
            mid = (low + high + 1) // 2
            success, _ = await self._run_concurrent(mid)
            success_rate = success / mid
            logger.debug(f"Burst test {mid}: {success_rate:.2%}")
            if success_rate > 0.95:
                low = mid
            else:
                high = mid - 1
        return low

    async def sustained_test(self) -> TestStats:
        """Measure over duration."""
        stats = TestStats()
        times = deque(maxlen=10)
        end_time = asyncio.get_event_loop().time() + self.config.duration

        while asyncio.get_event_loop().time() < end_time:
            start = asyncio.get_event_loop().time()
            success, fail = await self._run_concurrent(self.config.concurrency)
            elapsed = asyncio.get_event_loop().time() - start
            rps = success / elapsed
            times.append(rps)
            stats.total_requests += success + fail
            stats.successes += success
            stats.failures += fail
            stats.avg_rps = sum(times) / len(times)
            stats.peak_rps = max(stats.peak_rps or 0, rps)
            await asyncio.sleep(0.1)

        return stats

    async def measure_reset(self) -> float:
        """Hit limit, poll for reset."""
        # Simplified: run until 429, then poll
        async with RateLimitClient(self.config) as client:
            while True:
                resp = await client.get(self.config.url)
                if resp.status_code == 429:
                    retry_after = resp.headers.get("retry-after", 1)
                    start = asyncio.get_event_loop().time()
                    while True:
                        await asyncio.sleep(float(retry_after))
                        resp = await client.head(self.config.url)
                        if resp.status_code < 400:
                            return asyncio.get_event_loop().time() - start
                await asyncio.sleep(0.1)
