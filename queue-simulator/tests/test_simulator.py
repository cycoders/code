import pytest
import random

from queue_simulator.simulator import Simulator
from queue_simulator.distributions import get_service_sampler


@pytest.fixture
def fixed_sampler():
    return get_service_sampler("fixed", {"service_mean": 0.5}, random.Random(42))


class TestSimulator:
    def test_basic_fixed(self, fixed_sampler):
        sim = Simulator(num_workers=1, service_sampler=fixed_sampler)
        stats = sim.run(sim_duration=10.0, arrival_rate=1.0, seed=42)
        assert stats.completed_jobs >= 1
        assert stats.avg_latency >= 0.5
        assert stats.max_queue_len >= 0

    def test_no_arrivals(self, fixed_sampler):
        sim = Simulator(1, fixed_sampler)
        stats = sim.run(10.0, 0.0, 42)
        assert stats.completed_jobs == 0
        assert stats.max_queue_len == 0

    def test_zero_workers_invalid(self):
        with pytest.raises(ValueError):
            Simulator(0, lambda: 0.1)

    def test_overloaded_queue(self, fixed_sampler):
        # High arrival, low service? Fixed 0.5s service, arrival 3/s -> backlog
        sim = Simulator(1, fixed_sampler)
        stats = sim.run(5.0, 3.0, 42)
        assert stats.max_queue_len > 0
        assert stats.avg_queue_len > 0

    def test_multiple_workers(self, fixed_sampler):
        sim = Simulator(2, fixed_sampler)
        stats = sim.run(10.0, 2.0, 42)
        assert stats.utilization > 0
        assert stats.utilization <= 100

    def test_utilization(self, fixed_sampler):
        sim = Simulator(1, fixed_sampler)
        stats = sim.run(10.0, 1.0, 42)
        # ~50% util expected
        assert 30 < stats.utilization < 70  # approx