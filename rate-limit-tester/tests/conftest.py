import pytest
import respx
from httpx import Response


@pytest.fixture
async def mock_http():
    with respx.mock() as p:
        yield p
