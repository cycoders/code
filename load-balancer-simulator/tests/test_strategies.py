import pytest
from unittest.mock import Mock, patch
from load_balancer_simulator.strategies import RoundRobinSelector, LeastConnectionsSelector, RandomSelector, IPHashSelector, WeightedRRSelector
from load_balancer_simulator.backend import Backend


@pytest.fixture
def mock_backends():
    return [
        Backend({"name": "b1", "capacity": 10, "service_time_mean": 0.1, "service_time_std": 0, "failure_rate": 0, "weight": 1}),
        Backend({"name": "b2", "capacity": 10, "service_time_mean": 0.1, "service_time_std": 0, "failure_rate": 0, "weight": 1})
    ]


def test_round_robin(mock_backends):
    sel = RoundRobinSelector()
    b1 = sel.select(mock_backends)
    b2 = sel.select(mock_backends)
    assert b1 is mock_backends[0]
    assert b2 is mock_backends[1]


def test_least_connections(mock_backends):
    mock_backends[0].queue.append(("req", 0))  # load 1
    sel = LeastConnectionsSelector()
    selected = sel.select(mock_backends)
    assert selected is mock_backends[1]  # lower load


@patch('random.choice')
def test_random(mock_choice, mock_backends):
    mock_choice.return_value = mock_backends[0]
    sel = RandomSelector()
    assert sel.select(mock_backends) is mock_backends[0]


def test_ip_hash(mock_backends):
    sel = IPHashSelector()
    b = sel.select(mock_backends, "192.168.1.1")
    assert b in mock_backends  # deterministic


def test_weighted_rr(mock_backends):
    mock_backends[0].weight = 1
    mock_backends[1].weight = 2
    sel = WeightedRRSelector(mock_backends)
    seq = [sel.select(mock_backends) for _ in range(6)]
    assert seq.count(mock_backends[0]) == 2
    assert seq.count(mock_backends[1]) == 4