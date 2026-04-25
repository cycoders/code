import pytest
from circuit_breaker_simulator.models import SimulationConfig, BreakerConfig


def test_default_breakers():
    cfg = SimulationConfig()
    assert len(cfg.breakers) == 1
    assert cfg.breakers[0].name == "default"


def test_validation():
    with pytest.raises(ValueError):
        SimulationConfig(rps=-1)

    cfg = BreakerConfig(name="test", type="consecutive", consec_threshold=2)
    assert cfg.failure_threshold == 0  # ignored


def test_yaml_load():
    data = {
        "rps": 5.0,
        "breakers": [{"name": "foo", "type": "threshold", "failure_threshold": 10}]
    }
    cfg = SimulationConfig.model_validate(data)
    assert cfg.rps == 5.0
