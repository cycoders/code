import pytest
from cron_simulator.parser import parse_jobs
from cron_simulator.simulator import simulate_jobs, detect_overlaps
from datetime import datetime
from zoneinfo import ZoneInfo


def test_end_to_end():
    jobs = parse_jobs("examples/jobs.yaml")
    assert len(jobs) == 3

    start = datetime(2024, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
    end = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo("UTC"))

    execs = simulate_jobs(jobs, start, end)
    assert len(execs) > 20  # Hourly + daily

    overlaps = detect_overlaps(execs)
    assert len(overlaps) == 0  # No overlaps in example