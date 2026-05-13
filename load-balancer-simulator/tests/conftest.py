import pytest
import yaml
from load_balancer_simulator.config import Config


@pytest.fixture
def sample_config():
    return Config.model_validate({
        "duration": 1.0,
        "arrival_rate": 10.0,
        "dt": 0.1,
        "strategy": "round-robin",
        "backends": [
            {"name": "test", "capacity": 5, "service_time_mean": 0.1, "service_time_std": 0.01, "failure_rate": 0.0, "weight": 1}
        ]
    })


@pytest.fixture
def sample_yaml():
    return """
duration: 1.0
arrival_rate: 10.0
backends:
  - name: test
    capacity: 5
    service_time_mean: 0.1
    service_time_std: 0.01
"""
