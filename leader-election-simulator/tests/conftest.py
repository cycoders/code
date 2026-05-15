import pytest
import random

random.seed(42)

@pytest.fixture
def small_sim():
    from leader_election_simulator.simulator import Simulator
    return Simulator(
        num_nodes=3,
        seed=42,
        heartbeat_interval=10,
        election_timeout_min=5,
        election_timeout_max=10,
        failure_prob=0.0,
        recovery_prob=0.0,
        partition_prob=0.0,
    )

@pytest.fixture
def node():
    from leader_election_simulator.node import Node
    return Node("test", 5, 250, 500)