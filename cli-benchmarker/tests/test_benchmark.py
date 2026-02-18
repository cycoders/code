import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock

from cli_benchmarker.benchmark import benchmark_commands, run_once


@pytest.fixture
def mock_proc_success():
    mock_proc = Mock()
    mock_proc.poll.return_value = None
    mock_proc.returncode = 0
    mock_proc.pid = 1234
    mock_proc.communicate.return_value = (b"stdout", b"stderr")
    return mock_proc


@pytest.fixture
def mock_proc_fail():
    mock_proc = Mock()
    mock_proc.returncode = 1
    mock_proc.pid = 1234
    mock_proc.communicate.return_value = (b"", b"error")
    return mock_proc


class TestRunOnce:
    def test_success(self, mock_proc_success):
        with patch("subprocess.Popen", return_value=mock_proc_success):
            with patch("psutil.Process") as mock_psutil:
                mock_ct = Mock(user=0.1, system=0.05, children_user=0.0, children_system=0.0)
                mock_process = Mock(cpu_times=Mock(return_value=mock_ct))
                mock_process.memory_info.return_value = Mock(rss=100 * 1024 * 1024)
                mock_psutil.return_value = mock_process

                result = run_once(["echo", "hi"], 10.0, verbose=False)

                assert result["success"] is True
                assert result["cpu_total"] == 0.15
                assert result["mem_peak_mb"] > 0

    def test_failure(self, mock_proc_fail):
        with patch("subprocess.Popen", return_value=mock_proc_fail):
            with patch("psutil.Process") as mock_psutil:
                mock_process = Mock()
                mock_psutil.return_value = mock_process

                result = run_once(["false"], 10.0, verbose=False)
                assert result["success"] is False
                assert result["exit_code"] == 1

    def test_timeout(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = Mock()
            mock_popen.return_value = mock_proc
            mock_proc.communicate.side_effect = subprocess.TimeoutExpired("cmd", 1.0)

            result = run_once(["sleep", "100"], 0.1, verbose=False)
            assert result["success"] is False
            assert result["exit_code"] == -9


class TestBenchmarkCommands:
    def test_basic(self):
        with patch("cli_benchmarker.benchmark.run_once", return_value={"success": True, "wall_time": 0.1}):
            results = benchmark_commands(["echo"], warmup_runs=1, num_runs=3, timeout=1.0, verbose=False)
            assert len(results) == 3
            assert all(r["success"] for r in results)