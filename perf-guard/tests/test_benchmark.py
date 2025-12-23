import pytest
from unittest.mock import patch, MagicMock

from perf_guard.benchmark import run_benchmark


def test_run_benchmark_success(capsys):
    with patch("subprocess.run") as mock_run, patch("time.perf_counter") as mock_time:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        mock_time.side_effect = [0, 0.1, 0.2, 0.35]  # warmup1, bench1

        times = run_benchmark(["test"], iterations=1, warmup=1)

        assert len(times) == 1
        assert times[0] == 0.15  # 0.35-0.2


def test_run_benchmark_fail():
    with patch("subprocess.run") as mock_run:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_run.return_value = mock_proc

        with pytest.raises(RuntimeError, match="failed"):
            run_benchmark(["test"], iterations=1, warmup=0)


def test_script_not_found():
    with pytest.raises(FileNotFoundError):
        run_benchmark(["/nope"], iterations=1, warmup=0)