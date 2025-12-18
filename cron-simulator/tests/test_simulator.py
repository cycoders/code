import pytest
from datetime import datetime, timedelta, timezone
from cron_simulator.simulator import simulate_jobs, detect_overlaps
from cron_simulator.models import Job, Execution


@pytest.fixture
def utc():
    return timezone.utc


def test_simulate_single(utc):
    start = datetime(2024, 1, 1, 10, 0, tzinfo=utc)
    end = datetime(2024, 1, 1, 10, 6, tzinfo=utc)
    job = Job("test", "0/2 * * * *", duration=10)
    execs = simulate_jobs([job], start, end)
    assert len(execs) == 3
    assert execs[0].start == start
    assert execs[-1].end == datetime(2024, 1, 1, 10, 4, 10, tzinfo=utc)


def test_detect_overlaps():
    utc = timezone.utc
    e1 = Execution("j1", datetime(2024, 1, 1, 10, 0, tzinfo=utc), datetime(2024, 1, 1, 10, 5, tzinfo=utc))
    e2 = Execution("j2", datetime(2024, 1, 1, 10, 3, tzinfo=utc), datetime(2024, 1, 1, 10, 7, tzinfo=utc))
    e3 = Execution("j3", datetime(2024, 1, 1, 10, 8, tzinfo=utc), datetime(2024, 1, 1, 10, 9, tzinfo=utc))

    overlaps = detect_overlaps([e1, e2, e3])
    assert len(overlaps) == 1
    assert overlaps[0][1] == ["j1", "j2"]


def test_no_overlaps():
    e1 = Execution("j1", datetime(2024, 1, 1, 10, 0), datetime(2024, 1, 1, 10, 2))
    e2 = Execution("j2", datetime(2024, 1, 1, 10, 3), datetime(2024, 1, 1, 10, 4))
    assert detect_overlaps([e1, e2]) == []