import pytest

from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def mock_psutil_access(monkeypatch):
    """Mock access denied for realism."""
    monkeypatch.setattr("psutil.Process", Mock(side_effect=psutil.AccessDenied))


@pytest.fixture
def mock_connection():
    """Mock psutil connection factory."""
    from unittest.mock import Mock
    from collections import namedtuple

    Conn = namedtuple("Connection", ["laddr", "raddr", "status", "pid", "fd"])
    Addr = namedtuple("Addr", ["ip", "port"])

    return lambda **kwargs: Conn(
        laddr=Addr(**kwargs.get("l", {"ip": "127.0.0.1", "port": 8080})),
        raddr=Addr(**kwargs.get("r", {"ip": "127.0.0.1", "port": 54321})),
        status=kwargs.get("status", "ESTABLISHED"),
        pid=kwargs.get("pid", 1234),
        fd=5,
    )