import math
import random
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Dict, Any

from .policies import create_policy, RateLimiter, Decision


@dataclass
class SimulationConfig:
    duration: float
    rps: float
    num_keys: int
    policy_name: str
    policy_params: Dict[str, Any]
    burst_prob: float = 0.1


@dataclass
class Stats:
    hit_rate: float
    total_requests: int
    accepted: int
    rejected: int
    max_burst: int
    decisions: List[bool] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def generate_requests(
    duration: float,
    avg_rps: float,
    num_keys: int,
    burst_prob: float = 0.1,
) -> List[Tuple[float, str]]:
    """Generate Poisson process requests with optional bursts."""
    requests = []
    time = 0.0
    random.seed(42)  # Reproducible
    while time < duration:
        # Poisson inter-arrival
        if avg_rps > 0:
            inter_arrival = -math.log(random.random()) / avg_rps
        else:
            inter_arrival = 1.0
        time += inter_arrival
        if time > duration:
            break
        key = f"user{random.randint(1, num_keys)}"
        requests.append((time, key))
        # Burst: extra reqs
        if random.random() < burst_prob:
            burst_size = random.poisson(2)  # 0-5 extra
            for _ in range(int(burst_size)):
                requests.append((time + random.uniform(0, 0.01), f"user{random.randint(1, num_keys)}"))
    return requests


def run_simulation(config: SimulationConfig) -> Stats:
    """Run full simulation."""
    policy: RateLimiter = create_policy(config.policy_name, config.policy_params)
    requests = generate_requests(config.duration, config.rps, config.num_keys, config.burst_prob)

    now = 0.0
    accepted = 0
    rejected = 0
    current_burst = 0
    max_burst = 0
    decisions: List[bool] = []

    for req_time, key in requests:
        now = max(now, req_time)
        decision: Decision = policy.is_allowed(key, now)
        decisions.append(decision.allowed)
        if decision.allowed:
            accepted += 1
            current_burst += 1
            max_burst = max(max_burst, current_burst)
        else:
            rejected += 1
            current_burst = 0

    total = accepted + rejected
    hit_rate = accepted / total if total > 0 else 0.0

    return Stats(
        hit_rate=hit_rate,
        total_requests=total,
        accepted=accepted,
        rejected=rejected,
        max_burst=max_burst,
        decisions=decisions,
    )