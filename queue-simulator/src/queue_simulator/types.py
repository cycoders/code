from dataclasses import dataclass, field
from typing import List

def percentile(data: List[float], p: float) -> float:
    """Calculate percentile p (0-100)."""
    if not data:
        return 0.0
    data = sorted(data)
    index = (len(data) - 1) * (p / 100)
    floor = int(index)
    frac = index - floor
    if floor + 1 < len(data):
        return data[floor] + frac * (data[floor + 1] - data[floor])
    return data[floor]

from statistics import mean

@dataclass
class Stats:
    latencies: List[float] = field(default_factory=list)
    service_times: List[float] = field(default_factory=list)
    queue_times: List[float] = field(default_factory=list)
    queue_lens: List[int] = field(default_factory=list)
    max_queue_len: int = 0
    completed_jobs: int = 0
    sim_duration: float = 0.0
    num_workers: int = 0

    @property
    def avg_latency(self) -> float:
        return mean(self.latencies) if self.latencies else 0.0

    @property
    def p95_latency(self) -> float:
        return percentile(self.latencies, 95)

    @property
    def avg_queue_len(self) -> float:
        return mean(self.queue_lens) if self.queue_lens else 0.0

    @property
    def avg_service_time(self) -> float:
        return mean(self.service_times) if self.service_times else 0.0

    @property
    def throughput(self) -> float:
        return self.completed_jobs / self.sim_duration if self.sim_duration > 0 else 0.0

    @property
    def utilization(self) -> float:
        if not self.service_times or self.sim_duration == 0 or self.num_workers == 0:
            return 0.0
        total_busy_time = sum(self.service_times)
        total_available = self.num_workers * self.sim_duration
        return (total_busy_time / total_available) * 100

    def to_dict(self) -> dict:
        return {
            "avg_latency": self.avg_latency,
            "p95_latency": self.p95_latency,
            "avg_queue_len": self.avg_queue_len,
            "max_queue_len": self.max_queue_len,
            "throughput": self.throughput,
            "utilization": self.utilization,
            "avg_service_time": self.avg_service_time,
            "completed_jobs": self.completed_jobs,
        }