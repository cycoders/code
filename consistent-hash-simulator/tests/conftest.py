import pytest

@pytest.fixture
def sample_ring():
    return ConsistentHashRing(["node-0", "node-1"])