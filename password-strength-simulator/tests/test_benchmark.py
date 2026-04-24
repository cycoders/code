import pytest
import time
from unittest.mock import patch
from password_strength_simulator.benchmark import benchmark_algo, _hash_once


@pytest.mark.parametrize("algo", ["md5", "bcrypt", "argon2"])
def test_hash_once(algo: str):
    pw = b"test"
    salt = b"salt"
    result = _hash_once(algo, 12, pw, salt)
    assert isinstance(result, bytes)
    assert len(result) > 0


@patch("time.perf_counter")
@patch("multiprocessing.cpu_count", return_value=2)
def test_benchmark_algo(*mocks):
    def mock_time():
        t = [0]
        def inner():
            t[0] += 0.1
            return t[0]
        return inner

    with patch("password_strength_simulator.benchmark.time.perf_counter", mock_time()), patch(
        "concurrent.futures.ProcessPoolExecutor"
    ) as mock_exec:
        mock_future = mock_exec.return_value.__enter__.return_value.submit.return_value
        mock_future.result.return_value = 10  # 10 hashes

        log_hps = benchmark_algo("md5", 0, duration=0.2, num_processes=1)
        # Approx: 10 hashes / 0.2s = 50 H/s, log10~1.7
        assert log_hps > 0