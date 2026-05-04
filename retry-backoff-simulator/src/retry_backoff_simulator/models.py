from typing import List, Optional, Literal

from pydantic import BaseModel, Field, validator

import random
import statistics


class BackoffConfig(BaseModel):
    strategy: Literal["fixed", "exponential", "full_jitter", "equal_jitter", "decorrelated_jitter"] = "exponential"
    base_delay: float = Field(..., ge=0.0)
    factor: float = Field(2.0, ge=1.0)
    max_delay: float = Field(30.0, ge=0.0)
    max_attempts: int = Field(10, ge=1)


class SimConfig(BaseModel):
    backoff: BackoffConfig = Field(default_factory=BackoffConfig)
    failure_rate: float = Field(0.3, ge=0.0, le=1.0)
    service_time: float = Field(0.05, ge=0.0)
    num_trials: int = Field(1000, ge=1)
    seed: int = 42
    failure_sequence: Optional[List[bool]] = None


class TrialResult(BaseModel):
    total_time: float
    attempts: int
    success: bool


class Metrics(BaseModel):
    name: str = ""
    success_rate: float
    avg_attempts: float
    p50_attempts: float
    p95_attempts: float
    avg_time: float
    p50_time: float
    p95_time: float
    max_time: float


def aggregate_metrics(results: List[TrialResult], name: str = "") -> Metrics:
    successes = [r for r in results if r.success]
    num_success = len(successes)
    success_rate = num_success / len(results)

    all_attempts = [r.attempts for r in results]
    avg_attempts = statistics.mean(all_attempts)
    attempts_50 = statistics.median(all_attempts)
    attempts_95 = percentile(all_attempts, 95)

    all_times = [r.total_time for r in results]
    avg_time = statistics.mean(all_times)
    times_50 = statistics.median(all_times)
    times_95 = percentile(all_times, 95)
    max_time = max(all_times)

    return Metrics(
        name=name,
        success_rate=success_rate,
        avg_attempts=avg_attempts,
        p50_attempts=attempts_50,
        p95_attempts=attempts_95,
        avg_time=avg_time,
        p50_time=times_50,
        p95_time=times_95,
        max_time=max_time,
    )


def percentile(data: List[float], p: float) -> float:
    """Linear interpolation percentile."""
    if not data:
        return 0.0
    data = sorted(data)
    i = (len(data) - 1) * p / 100.0
    j = int(i)
    fraction = i - j
    if j + 1 >= len(data):
        return data[j]
    return data[j] + fraction * (data[j + 1] - data[j])
