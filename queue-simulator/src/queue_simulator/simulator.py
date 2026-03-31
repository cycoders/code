import heapq
import random
from pathlib import Path
from typing import List, Tuple, Optional

from .types import Stats
from .distributions import get_service_sampler

class Job:
    __slots__ = ["arrival_time", "start_time", "end_time", "service_time"]

    def __init__(self, arrival_time: float):
        self.arrival_time = arrival_time
        self.start_time = 0.0
        self.end_time = 0.0
        self.service_time = 0.0

class Simulator:
    def __init__(self, num_workers: int, service_sampler: 'Callable[[], float]'):
        if num_workers < 1:
            raise ValueError("num_workers must be >=1")
        self.num_workers = num_workers
        self.service_sampler = service_sampler
        self.stats = Stats(num_workers=num_workers)

    def run(
        self,
        sim_duration: float,
        arrival_rate: float,
        seed: Optional[int] = None,
    ) -> Stats:
        if sim_duration <= 0:
            raise ValueError("sim_duration must be >0")
        if arrival_rate < 0:
            raise ValueError("arrival_rate must be >=0")

        self.stats.sim_duration = sim_duration
        rng = random.Random(seed)

        current_time = 0.0
        event_queue: List[Tuple[float, str, Optional[Job]]] = []
        pending_queue: List[Job] = []
        busy_workers = 0
        self.stats.max_queue_len = 0

        # First arrival
        next_arrival_time = rng.expovariate(arrival_rate)
        heapq.heappush(event_queue, (next_arrival_time, "arrival", None))

        while event_queue:
            event_time, event_type, job = heapq.heappop(event_queue)
            if event_time > sim_duration:
                break
            current_time = event_time

            if event_type == "arrival":
                new_job = Job(current_time)
                pending_queue.append(new_job)
                self.stats.max_queue_len = max(self.stats.max_queue_len, len(pending_queue))
                self._record_queue_len(current_time, len(pending_queue))

                # Schedule next arrival
                next_arrival_delta = rng.expovariate(arrival_rate)
                next_arrival = current_time + next_arrival_delta
                if next_arrival <= sim_duration:
                    heapq.heappush(event_queue, (next_arrival, "arrival", None))

            elif event_type == "end_job":
                busy_workers -= 1
                self.stats.completed_jobs += 1
                job.end_time = current_time
                latency = current_time - job.arrival_time
                self.stats.latencies.append(latency)

            # Try to start jobs if workers available
            while busy_workers < self.num_workers and pending_queue:
                job = pending_queue.pop(0)
                job.start_time = current_time
                service_time = self.service_sampler()
                job.service_time = service_time
                self.stats.service_times.append(service_time)
                end_time = current_time + service_time
                heapq.heappush(event_queue, (end_time, "end_job", job))
                busy_workers += 1
                self.stats.max_queue_len = max(self.stats.max_queue_len, len(pending_queue))
                self._record_queue_len(current_time, len(pending_queue))

        return self.stats

    def _record_queue_len(self, time: float, queue_len: int):
        self.stats.queue_times.append(time)
        self.stats.queue_lens.append(queue_len)