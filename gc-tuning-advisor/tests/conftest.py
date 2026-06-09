import pytest

@pytest.fixture
def sample_log():
    return ['gen 0 collected 1200 uncollectable 0 took 1.2ms']