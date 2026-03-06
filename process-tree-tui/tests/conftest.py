import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_psutil_errors():
    """Mock common psutil errors for safe testing."""
    with patch("psutil.NoSuchProcess") as m:
        m.side_effect = psutil.NoSuchProcess
        yield m


@pytest.fixture
def mock_process():
    """Basic mock process."""
    p = MagicMock()
    p.pid = 123
    p.ppid.return_value = 1
    p.name.return_value = "testproc"
    p.cpu_percent.return_value = 1.23
    p.memory_info.return_value = MagicMock(rss=104857600)  # 100MB
    p.cmdline.return_value = ["test", "proc"]
    p.info = {
        "pid": 123,
        "ppid": 1,
        "name": "testproc",
        "cpu_percent": 1.23,
        "cmdline": ["test", "proc"],
    }
    return p