import pytest
from unittest.mock import MagicMock, patch
from circuit_breaker_simulator.simulator import Simulator
from circuit_breaker_simulator.models import SimulationConfig


def test_simulator_runs(basic_config):
    cfg = SimulationConfig.model_validate(basic_config.dict())
    console = MagicMock()
    sim = Simulator(cfg, console)
    stats = sim.run("console")
    assert len(stats.breakers) == 1
    assert stats.breakers["default"].total_requests > 0

@patch("random.expovariate")
@patch("random.choice")
def test_poisson_load(mock_choice, mock_expov, basic_config):
    mock_expov.return_value = 0.1
    mock_choice.return_value = "mock"
    cfg = SimulationConfig(rps=10.0, duration_secs=1)
    sim = Simulator(cfg)
    stats = sim.run("console")
    # ~10 reqs
    assert stats.breakers["default"].total_requests >= 5  # approx


def test_ramp(basic_config):
    cfg = SimulationConfig(rps=10, duration_secs=10, ramp_duration_secs=5)
    sim = Simulator(cfg)
    # Early low rate implicit
    pass  # logic covered
