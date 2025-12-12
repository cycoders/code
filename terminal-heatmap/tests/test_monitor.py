import time
import psutil
from unittest.mock import MagicMock, patch
from terminal_heatmap.monitor import ProcessMonitor


@patch("psutil.cpu_count")
@patch("psutil.process_iter")
def test_process_monitor_sample(mock_iter, mock_cpu_count) -> None:
    mock_cpu_count.return_value = 4

    class MockProc:
        def info(self):
            return {
                "pid": 1234,
                "name": "testproc",
                "cpu_times": MagicMock(utime=10.0, stime=2.0),
                "memory_percent": 5.2,
            }

    mock_iter.return_value = [MockProc()]

    monitor = ProcessMonitor()
    # First sample: empty
    procs = monitor.sample()
    assert len(procs) == 0

    # Second: populated
    time.sleep(0.01)  # small delta
    procs = monitor.sample()
    assert len(procs) == 1
    assert procs[0]["pid"] == 1234
    assert procs[0]["name"].startswith("testproc")
    assert procs[0]["cpu_percent"] >= 0


@patch("psutil.cpu_count")
def test_process_monitor_system_stats(mock_cpu_count) -> None:
    monitor = ProcessMonitor()
    stats = monitor.get_system_stats()
    assert "cpu_percent" in stats
    assert "mem_percent" in stats
    assert stats["mem_used_gb"] >= 0
    assert stats["mem_total_gb"] > 0