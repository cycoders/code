import pytest
from unittest.mock import Mock, patch

import psutil

from netmon_tui.fetchers import get_connections, get_interface_stats
from netmon_tui.models import Addr, Connection


@patch("psutil.net_connections")
@patch("psutil.Process")
def test_get_connections_tcp(mock_proc, mock_net_conns):
    """Test TCP connection fetch."""

    mock_conn = Mock()
    mock_conn.laddr.ip = "127.0.0.1"
    mock_conn.laddr.port = 8080
    mock_conn.raddr.ip = "93.184.216.34"
    mock_conn.raddr.port = 443
    mock_conn.status = "ESTABLISHED"
    mock_conn.pid = 1234
    mock_net_conns.return_value = [mock_conn]

    mock_proc.return_value.name.return_value = "python"

    conns = asyncio.run(get_connections())

    assert len(conns) == 1
    c = conns[0]
    assert c.local == Addr("127.0.0.1", 8080)
    assert c.raddr == Addr("93.184.216.34", 443)
    assert c.status == "ESTABLISHED"
    assert c.pid == 1234
    assert c.process_name == "python"


@patch("psutil.net_connections")
def test_get_connections_no_pid(mock_net_conns):
    """Test no PID/kernel conn."""

    mock_conn = Mock(pid=None, raddr=None)
    mock_net_conns.return_value = [mock_conn]

    conns = asyncio.run(get_connections())
    assert len(conns) == 0  # skipped no raddr


@patch("psutil.net_connections")
def test_get_connections_access_denied(mock_net_conns, mock_proc):
    """Test AccessDenied graceful."""

    mock_conn = Mock(pid=999)
    mock_net_conns.return_value = [mock_conn]
    mock_proc.side_effect = psutil.AccessDenied

    conns = asyncio.run(get_connections())
    assert len(conns) == 1
    assert conns[0].process_name is None


@patch("psutil.net_io_counters")
def test_get_interface_stats(mock_counters):
    """Test interface stats fetch."""

    mock_snetio = Mock()
    mock_snetio._asdict.return_value = {
        "bytes_sent": 1024**2,
        "bytes_recv": 1024**3,
        "packets_sent": 100,
        "packets_recv": 200,
        "errin": 0,
        "errout": 0,
        "dropin": 0,
        "dropout": 0,
    }
    mock_counters.return_value = {"lo": mock_snetio}

    stats = asyncio.run(get_interface_stats())
    assert len(stats) == 1
    assert stats["lo"]["bytes_sent"] == 1024**2


@patch("psutil.net_io_counters")
def test_get_interface_stats_empty(mock_counters):
    """Empty interfaces."""

    mock_counters.side_effect = psutil.NoSuchProcess
    stats = asyncio.run(get_interface_stats())
    assert stats == {}