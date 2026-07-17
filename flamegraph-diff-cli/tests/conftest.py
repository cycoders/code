import pytest

@pytest.fixture
def sample_stacks():
    return {'main;foo': 10}, {'main;foo': 20}