import asyncio
import pytest
import time

from connection_pool_simulator.config import SimConfig
from connection_pool_simulator.simulator import run_simulation


@pytest.mark.asyncio
async def test_run_simulation_basic():
    cfg = SimConfig(
        max_size=2,
        num_clients=4,
        requests_per_client=5,
        query_duration_mean=0.001,
        query_duration_std=0.0,
        ramp_up_duration=0.0,
        acquire_timeout=0.1,
    )
    metrics = await run_simulation(cfg)
    assert metrics["total_requests"] == 20
    assert metrics["throughput"] > 100  # Fast
    assert metrics["utilization_pct"] > 0
    assert metrics["reject_rate_pct"] < 10  # Some rejects expected


@pytest.mark.asyncio
async def test_no_rejects_large_pool():
    cfg = SimConfig(
        max_size=10,
        num_clients=5,
        requests_per_client=10,
        query_duration_mean=0.001,
        query_duration_std=0.0,
        ramp_up_duration=0.0,
        acquire_timeout=10.0,
    )
    metrics = await run_simulation(cfg)
    assert metrics["rejected"] == 0
    assert metrics["reject_rate_pct"] == 0.0


@pytest.mark.asyncio
async def test_timeout_rejects():
    cfg = SimConfig(
        max_size=1,
        num_clients=10,
        requests_per_client=3,
        query_duration_mean=0.05,
        query_duration_std=0.0,
        ramp_up_duration=0.0,
        acquire_timeout=0.01,
    )
    metrics = await run_simulation(cfg)
    assert metrics["rejected"] > 0
    assert metrics["reject_rate_pct"] > 0


@pytest.mark.asyncio
async def test_p95_wait():
    cfg = SimConfig(
        max_size=5,
        num_clients=10,
        requests_per_client=20,
        query_duration_mean=0.001,
        query_duration_std=0.0005,
        ramp_up_duration=0.0,
        acquire_timeout=1.0,
    )
    metrics = await run_simulation(cfg)
    assert metrics["p95_wait_time"] >= 0
    assert metrics["avg_wait_time"] >= 0


@pytest.mark.asyncio
async def test_utilization_calc():
    cfg = SimConfig(
        max_size=1,
        num_clients=1,
        requests_per_client=1,
        query_duration_mean=0.1,
        query_duration_std=0.0,
        ramp_up_duration=0.0,
        acquire_timeout=1.0,
    )
    metrics = await run_simulation(cfg)
    # Single long query, util ~100%
    assert metrics["utilization_pct"] >= 90
