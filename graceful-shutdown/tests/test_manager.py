import asyncio
import pytest
from graceful_shutdown import ShutdownManager

@pytest.mark.asyncio
async def test_basic_lifecycle():
    mgr = ShutdownManager(timeout=1.0)
    with mgr():
        assert not mgr.cancelled

@pytest.mark.asyncio
async def test_signal_sets_cancel():
    mgr = ShutdownManager(timeout=0.1)
    mgr._trigger()
    assert mgr.cancelled

@pytest.mark.asyncio
async def test_timeout_path():
    mgr = ShutdownManager(timeout=0.01)
    with mgr():
        await asyncio.sleep(0.02)
    assert True  # reached without hang

@pytest.mark.asyncio
async def test_multiple_signals():
    mgr = ShutdownManager()
    mgr._trigger()
    mgr._trigger()
    assert mgr.cancelled

def test_version():
    from graceful_shutdown import __version__
    assert __version__.startswith("0.")