import pytest

@pytest.fixture
def sample_async_code():
    return "async def main(): import time; time.sleep(0)"