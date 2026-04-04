import asyncio
import random
import statistics
import time
from typing import Dict, List, Any

from .config import SimConfig


class MetricsCollector:
    def __init__(self) -> None:
        self.wait_times: List[float] = []
        self.query_times: List[float] = []
        self.rejects: int = 0
        self.fails: int = 0
        self._lock = asyncio.Lock()

    async def record_wait(self, wait_time: float) -> None:
        async with self._lock:
            self.wait_times.append(wait_time)

    async def record_query(self, query_time: float) -> None:
        async with self._lock:
            self.query_times.append(query_time)

    async def increment_reject(self) -> None:
        async with self._lock:
            self.rejects += 1

    async def increment_fail(self) -> None:
        async with self._lock:
            self.fails += 1

    async def get_snapshot(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "wait_times": self.wait_times[:],
                "query_times": self.query_times[:],
                "rejects": self.rejects,
                "fails": self.fails,
            }


async def client_task(
    client_id: int,
    semaphore: asyncio.Semaphore,
    collector: MetricsCollector,
    config: SimConfig,
    start_delay: float,
) -> None:
    await asyncio.sleep(start_delay)
    for _ in range(config.requests_per_client):
        acquire_start = time.perf_counter()
        try:
            async with asyncio.timeout(config.acquire_timeout):
                await semaphore.acquire()
            wait_time = time.perf_counter() - acquire_start
            await collector.record_wait(wait_time)

            query_start = time.perf_counter()
            duration = max(0.0, random.gauss(config.query_duration_mean, config.query_duration_std))
            await asyncio.sleep(duration)
            query_time = time.perf_counter() - query_start
            await collector.record_query(query_time)

            semaphore.release()
        except asyncio.TimeoutError:
            await collector.increment_reject()
        except Exception:
            await collector.increment_fail()


def _compute_metrics(
    snapshot: Dict[str, Any],
    total_requests: int,
    total_time: float,
    max_size: int,
) -> Dict[str, float]:
    wait_times = snapshot["wait_times"]
    query_times = snapshot["query_times"]
    rejects = snapshot["rejects"]
    fails = snapshot["fails"]

    successful = total_requests - rejects - fails
    throughput = successful / total_time if total_time > 0 else 0.0

    avg_wait = statistics.mean(wait_times) if wait_times else 0.0
    if wait_times:
        sorted_waits = sorted(wait_times)
        p95_idx = max(0, min(len(sorted_waits) - 1, int(len(sorted_waits) * 0.95)))
        p95_wait = sorted_waits[p95_idx]
    else:
        p95_wait = 0.0

    avg_query = statistics.mean(query_times) if query_times else 0.0
    total_busy = sum(query_times)
    utilization = min(100.0, (total_busy / total_time / max_size * 100) if total_time > 0 else 0.0)
    reject_rate = (rejects / total_requests * 100) if total_requests > 0 else 0.0

    return {
        "total_requests": total_requests,
        "successful": successful,
        "rejected": rejects,
        "failed": fails,
        "total_time": total_time,
        "throughput": throughput,
        "avg_wait_time": avg_wait,
        "p95_wait_time": p95_wait,
        "avg_query_time": avg_query,
        "utilization_pct": utilization,
        "reject_rate_pct": reject_rate,
    }


async def run_simulation(config: SimConfig) -> Dict[str, Any]:
    """Run pool simulation, return metrics dict."""
    collector = MetricsCollector()
    semaphore = asyncio.Semaphore(config.max_size)

    sim_start = time.perf_counter()
    tasks: List[asyncio.Task] = []
    ramp_step = config.ramp_up_duration / max(1, config.num_clients)

    for client_id in range(config.num_clients):
        delay = client_id * ramp_step
        task = asyncio.create_task(
            client_task(client_id, semaphore, collector, config, delay)
        )
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)
    sim_end = time.perf_counter()

    total_time = sim_end - sim_start
    total_requests = config.num_clients * config.requests_per_client

    snapshot = await collector.get_snapshot()
    metrics = _compute_metrics(snapshot, total_requests, total_time, config.max_size)

    return metrics
