import pytest
from thread_pool_calibrator.simulator import DiscreteEventSimulator

def test_simulator_basic():
    sim = DiscreteEventSimulator({"io_ratio": 0.7})
    r = sim.run(8)
    assert "p95" in r and r["p95"] > 0

def test_simulator_edge_zero_pool():
    sim = DiscreteEventSimulator({})
    r = sim.run(0)
    assert r["throughput"] == 0