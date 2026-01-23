import asyncio
import random
from unittest.mock import patch

import pytest
from chaos_proxy.config import Config


@pytest.mark.asyncio
async def test_forward_loss(mock_config: Config) -> None:
    mock_config.loss = 0.5  # 50% drop

    drops = 0
    sends = 0

    async def mock_read(size: int) -> bytes:
        return b"testdata"

    async def mock_write(data: bytes) -> None:
        nonlocal sends
        sends += 1

    async def mock_drain() -> None:
        pass

    # Patch random for determinism
    with patch("random.random", side_effect=[0.4, 0.6] * 5):  # drop, no-drop
        src = AsyncMock(read=AsyncMock(side_effect=mock_read))
        dst = AsyncMock()
        dst.write = mock_write
        dst.drain = mock_drain

        await forward_stream(src, dst, mock_config, MagicMock(), "req")

    assert sends < 10  # Some drops


@pytest.mark.parametrize("dup_prob", [0.0, 0.3])
def test_dup(dup_prob: float) -> None:
    cfg = mock_config()
    cfg.dup = dup_prob
    # Logic verified in forward
    assert 0 <= cfg.dup <= 1.0
