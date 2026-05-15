import pytest

from leader_election_simulator.simulator import Simulator


@pytest.mark.parametrize("steps", [20, 50, 100])
def test_sim_basic_election(small_sim, steps):
    """Sim elects a leader."""
    for _ in range(steps):
        small_sim.step()
    states = list(small_sim.history[-1].values())
    num_leaders = states.count("leader")
    assert num_leaders == 1, f"Expected 1 leader, got {num_leaders}: {states}"


def test_no_multiple_leaders(small_sim):
    """Never >1 leader."""
    for _ in range(200):
        small_sim.step()
        current = small_sim.history[-1]
        leaders = sum(1 for s in current.values() if s == "leader")
        assert leaders <= 1


def test_failure_injection(small_sim):
    """Failures toggle active."""
    small_sim._failure_prob = 0.5  # force for test
    for _ in range(10):
        small_sim.step()
    failed = sum(1 for n in small_sim.nodes.values() if not n.is_active)
    assert failed > 0


def test_partition_split(small_sim):
    """Partitions can split."""
    small_sim._partition_prob = 1.0  # force
    small_sim.step()
    assert len(small_sim.partitions) == 2


def test_export(capsys, small_sim):
    small_sim.run(10)
    fp = "test.json"
    small_sim.export(fp)
    import os
    assert os.path.exists(fp)
    os.unlink(fp)