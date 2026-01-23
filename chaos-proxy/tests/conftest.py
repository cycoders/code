import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_config():
    from chaos_proxy.config import Config
    return Config(
        target_host="127.0.0.1",
        target_port=80,
        local_port=8080,
        latency=0.1,
        jitter=0.0,
        loss=0.0,
        dup=0.0,
        bw_kbps=float("inf"),
    )
