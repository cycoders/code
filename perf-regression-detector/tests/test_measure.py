import pytest
from unittest.mock import Mock, patch

from perf_regression_detector.measure import compute_stats, run_single


@pytest.fixture
def mock_popen():
    p = Mock()
    p.poll.return_value = None
    p.poll.side_effect = [None, None, 0]
    p.returncode = 0
    p.cpu_times.return_value = Mock(user=0.01, system=0.0)
    return p


def test_compute_stats():
    values = [1.0, 1.2, 0.8]
    stats = compute_stats(values)
    assert stats["mean"] == 1.0
    assert abs(stats["std"] - 0.168) < 0.01


def test_run_single_timeout():
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = Mock(pid=123)
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        with patch("psutil.Process"):
            wt, ct, mem, rc, err = run_single(
                Mock(iterations=1, timeout=0.001, command="sleep", args=["0.1"])
            )
            assert err == "TIMEOUT"
            assert rc == -9