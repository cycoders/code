import asyncio
import time
from typing import Dict, Any, List
from rich.progress import (
    Progress,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TextColumn,
)

from reqbench.clients import create_async_session, create_sync_session
from reqbench.models import BenchmarkConfig
from reqbench.stats import compute_stats

class Benchmarker:
    def __init__(self, config: BenchmarkConfig):
        self.config = config

    def run(self) -> Dict[str, Dict[str, Any]]:
        """Run benchmark synchronously."""
        return asyncio.run(self._run_benchmark())

    async def _run_benchmark(self) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            for client_name in self.config.clients:
                task_id = progress.add_task(f"[cyan]{client_name}", total="dynamic")
                result = await self._benchmark_client(client_name, progress, task_id)
                results[client_name] = result
                progress.update(task_id, completed="done")
        return results

    async def _benchmark_client(
        self, client_name: str, progress: Progress, task_id: str
    ) -> Dict[str, Any]:
        latencies: List[float] = []
        total_requests = 0
        errors = 0
        end_time = time.perf_counter() + self.config.duration

        # Create session
        try:
            if client_name in ["httpx", "aiohttp"]:
                request_func, session = await create_async_session(client_name)
                close_session = session.aclose
            else:
                request_func, session = create_sync_session(client_name)
                async def async_request(req: Dict[str, Any]) -> Dict[str, Any]:
                    return await asyncio.to_thread(request_func, req)
                request_func = async_request
                def close_session() -> None:
                    session.close()
        except Exception as e:
            raise RuntimeError(f"Failed to create session for {client_name}: {e}")

        req_dict = self.config.model_dump(exclude={"clients", "concurrency", "duration"})

        semaphore = asyncio.Semaphore(self.config.concurrency)

        async def worker():
            nonlocal total_requests, errors
            while time.perf_counter() < end_time:
                async with semaphore:
                    try:
                        resp = await request_func(req_dict)
                        latencies.append(resp["latency"])
                        if not resp["ok"]:
                            errors += 1
                        total_requests += 1
                        progress.update(task_id, advance=1)
                    except Exception:
                        errors += 1
                        total_requests += 1
                        progress.update(task_id, advance=1)
                await asyncio.sleep(0.001)  # Yield

        workers = [
            asyncio.create_task(worker()) for _ in range(self.config.concurrency)
        ]
        await asyncio.sleep(self.config.duration)
        for w in workers:
            w.cancel()
        try:
            await asyncio.gather(*workers, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        finally:
            await asyncio.to_thread(close_session)

        return compute_stats(latencies, self.config.duration, total_requests, errors)