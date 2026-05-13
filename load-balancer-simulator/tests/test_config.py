import pytest
from load_balancer_simulator.config import Config, BackendConfig


def test_config_validation():
    cfg = Config(
        duration=60.0,
        arrival_rate=50.0,
        backends=[BackendConfig(name="b1", capacity=10, service_time_mean=0.05)]
    )
    assert cfg.arrival_rate == 50.0


def test_invalid_strategy():
    with pytest.raises(ValueError):
        Config(strategy="invalid")


def test_no_backends():
    with pytest.raises(ValueError):
        Config(backends=[])


def test_negative_capacity():
    with pytest.raises(ValueError):
        BackendConfig(capacity=-1)