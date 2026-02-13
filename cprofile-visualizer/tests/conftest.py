import pytest
import sys
from pathlib import Path
from cProfile import Profile


@pytest.fixture(scope="session")
def sample_prof(tmp_path: Path) -> Path:
    """Generate a realistic .prof file with fib-like calls."""
    prof_path = tmp_path / "test.prof"

    pr = Profile()
    pr.enable()

    def slow_func(n: int) -> int:
        if n < 2:
            return n
        return slow_func(n - 1) + slow_func(n - 2) + sum(range(10))

    slow_func(10)  # ~100 calls
    pr.disable()
    pr.dump_stats(str(prof_path))

    assert prof_path.exists() and prof_path.stat().st_size > 0
    return prof_path
