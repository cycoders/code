import random
import re
import pytest
from unittest.mock import patch, MagicMock

from redos_detector.fuzzer import Fuzzer


@pytest.fixture
def vuln_fuzzer():
    random.seed(42)
    return Fuzzer(r"^(a+)+$", timeout=0.05)


@pytest.fixture
def safe_fuzzer():
    random.seed(42)
    return Fuzzer(r"^\\d{3}-\\d{2}-\\d{4}$", timeout=0.1)


def test_match_time_safe(safe_fuzzer):
    """Safe regex completes fast."""
    time_taken = safe_fuzzer.match_time("123-45-6789")
    assert time_taken < 0.05


@pytest.fixture
def mock_timeout_executor():
    with patch("concurrent.futures.ThreadPoolExecutor") as mock:
        instance = MagicMock()
        instance.submit.return_value.result.side_effect = TimeoutError
        mock.return_value.__enter__.return_value = instance
        yield mock


def test_match_time_timeout(mock_timeout_executor, vuln_fuzzer):
    """Timeout returns > timeout."""
    long_str = "a" * 1000
    time_taken = vuln_fuzzer.match_time(long_str)
    assert time_taken > vuln_fuzzer.timeout


def test_generate_initial_repeat_heavy():
    """Initials have repeats."""
    f = Fuzzer("test")
    s = f.generate_initial(50)
    assert len(s) == 50
    # Has runs >2
    runs = [len(m.group(0)) for m in re.finditer(r"(. )\1+", re.escape(s))]
    assert any(r > 2 for r in runs)  # rough check


def test_mutate_increases_repeats(vuln_fuzzer):
    s = "aaa"
    mutated = vuln_fuzzer.mutate(s)
    assert len(mutated) >= len(s)


def test_fuzz_detects_vulnerable(vuln_fuzzer):
    """Detects known vuln with seed."""
    result = vuln_fuzzer.fuzz(max_generations=20, population_size=30)
    assert result["vulnerable"]
    assert result["max_time"] > 0.1
    assert len(result["worst_input"]) > 100


def test_fuzz_safe_not_vulnerable(safe_fuzzer):
    """Safe stays safe."""
    result = safe_fuzzer.fuzz(max_generations=10, population_size=20)
    assert not result["vulnerable"]
    assert result["max_time"] < 0.05


def test_fuzzer_invalid_regex():
    """Handled in CLI."""
    with pytest.raises(re.error):
        Fuzzer("[unclosed")
