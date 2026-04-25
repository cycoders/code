from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class BreakerStats:
    total_requests: int = 0
    rejects: int = 0
    service_calls: int = 0
    successes: int = 0
    service_failures: int = 0
    open_durations: List[float] = field(default_factory=list)  # cumulative secs open
    latencies: List[float] = field(default_factory=list)

    @property
    def reject_rate(self) -> float:
        return (self.rejects / max(self.total_requests, 1)) * 100

    @property
    def service_failure_rate(self) -> float:
        return (self.service_failures / max(self.service_calls, 1)) * 100

    @property
    def avg_latency(self) -> float:
        return sum(self.latencies) / max(len(self.latencies), 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "rejects": self.rejects,
            "reject_rate_pct": round(self.reject_rate, 2),
            "service_calls": self.service_calls,
            "successes": self.successes,
            "service_failures": self.service_failures,
            "service_failure_rate_pct": round(self.service_failure_rate, 2),
            "avg_latency_ms": round(self.avg_latency, 2),
            "total_open_secs": sum(self.open_durations),
        }

class SimulationStats:
    breakers: Dict[str, BreakerStats] = field(default_factory=dict)

    def add_open_duration(self, breaker_name: str, duration: float):
        self.breakers[breaker_name].open_durations.append(duration)

    def record_latency(self, breaker_name: str, latency: float):
        self.breakers[breaker_name].latencies.append(latency)

    def to_dict(self) -> Dict[str, Any]:
        return {name: stats.to_dict() for name, stats in self.breakers.items()}
