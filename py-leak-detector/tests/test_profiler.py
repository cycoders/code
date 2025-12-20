import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from py_leak_detector.profiler import monitor_script

@pytest.mark.parametrize("duration,expected_calls", [(0.1, 1), (1.0, 3)])
@patch("subprocess.Popen")
@patch("psutil.Process")
def test_monitor_rss(mock_psutil, mock_popen, mock_tracemalloc, tmp_path):
    mock_proc = MagicMock()
    mock_mem1 = MagicMock(rss=50 * 1024**2)
    mock_mem2 = MagicMock(rss=80 * 1024**2)
    mock_proc.memory_info.side_effect = [mock_mem1, mock_mem2]
    mock_psutil.return_value = mock_proc

    mock_popen.return_value = MagicMock(pid=1234)

    script_path = tmp_path / "test.py"
    script_path.touch()

    console = MagicMock()
    monitor_script(console, script_path, [], 1.0, 0.2, 20*1024**2, 1*1024**2, tmp_path)

    assert mock_popen.called
    assert mock_proc.memory_info.called
    assert len(mock_tracemalloc.call_count) >= 1  # snapshots triggered
