import pytest
import sys
from pathlib import Path

@pytest.fixture(autouse=True)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_tracemalloc(mocker):
    mock_snap = mocker.Mock()
    mock_snap.dump.return_value = None
    mock_snap.load.return_value = mock_snap
    mock_snap.compare_to.return_value = []
    mocker.patch("tracemalloc.Snapshot", return_value=mock_snap)
    mocker.patch("tracemalloc.start")
    mocker.patch("tracemalloc.take_snapshot", return_value=mock_snap)
    return mocker

@pytest.fixture
def mock_psutil(mocker):
    mock_proc = mocker.Mock()
    mock_mem = mocker.Mock()
    mock_mem.rss = 100 * 1024 * 1024
    mock_proc.memory_info.return_value = mock_mem
    return mock_proc
