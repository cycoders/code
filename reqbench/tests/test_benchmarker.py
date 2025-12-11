import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from reqbench.benchmarker import Benchmarker
from reqbench.models import BenchmarkConfig


@pytest.mark.asyncio
async def test_benchmarker_runs():
    config = BenchmarkConfig(url="https://example.com")
    with patch("reqbench.benchmarker.create_async_session", new=AsyncMock(return_value=(AsyncMock(), MagicMock()))):
        with patch("reqbench.benchmarker.create_sync_session", new=MagicMock()):
            bm = Benchmarker(config)
            results = await bm._run_benchmark()
            assert isinstance(results, dict)
            assert len(results) == len(config.clients)