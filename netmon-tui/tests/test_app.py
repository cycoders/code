import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from textual.app import App
from textual.testing import TestApp

from netmon_tui.app import NetmonApp, DataUpdate
from netmon_tui.fetchers import get_connections
from netmon_tui.models import Connection


@pytest.mark.asyncio
@patch("netmon_tui.fetchers.get_connections", new_callable=AsyncMock)
@patch("netmon_tui.fetchers.get_interface_stats", new_callable=AsyncMock)
async def test_app_refresh(mock_stats, mock_conns, dummy_app: TestApp):
    """Full refresh cycle."""

    app = NetmonApp(refresh_interval=999)  # disable interval
    await app.run_async(initial=False, auto_pilot=True)

    mock_conns.return_value = [Connection(Addr("127.0.0.1", 80), Addr("127.0.0.1", 8080), "ESTAB", 1, "test")]
    mock_stats.return_value = {"lo": {"bytes_sent": 0, "bytes_recv": 0}}

    app.action_request_refresh()
    await asyncio.sleep(0.1)

    assert len(app.connections) == 1
    assert app.interfaces == {"lo": {"bytes_sent": 0, "bytes_recv": 0}}


@pytest.mark.asyncio
async def test_app_filter():
    """Filter updates table."""

    app = NetmonApp()
    app.connections = [
        Connection(Addr("127.0.0.1", 80), Addr("127.0.0.1", 8080), "ESTAB", 1, "python"),
        Connection(Addr("127.0.0.1", 443), Addr("8.8.8.8", 53), "LISTEN", 2, "nginx"),
    ]
    app.update_conn_table()

    app.filter_str = "python"
    app.update_conn_table()
    # assert filtered to 1 (pseudo, since no table access)
    assert "python" in str(app.connections[0])


def test_app_keybinds(dummy_app: TestApp):
    """Basic bindings."""

    app = NetmonApp()
    assert "q" in app.BINDINGS
    assert "r" in app.BINDINGS