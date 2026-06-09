import pytest

@pytest.fixture
def sample_code():
    return 'asyncio.create_task(foo())'