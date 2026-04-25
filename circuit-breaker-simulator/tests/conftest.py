import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from circuit_breaker_simulator.models import SimulationConfig

@pytest.fixture
def basic_config():
    return SimulationConfig(rps=1.0, duration_secs=1, error_rate=0.5)
