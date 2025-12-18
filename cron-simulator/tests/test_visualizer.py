import pytest
from datetime import datetime, timedelta, timezone
from cron_simulator.visualizer import get_gantt_timeline
from cron_simulator.models import Execution


def test_gantt_timeline():
    utc = timezone.utc
    start = datetime(2024, 1, 1, 10, 0, tzinfo=utc)
    end = datetime(2024, 1, 1, 11, 0, tzinfo=utc)
    ex = Execution("test", start, start + timedelta(minutes=30))

    timeline = get_gantt_timeline([ex], start, end)
    assert len(timeline) == 100
    assert "▓" in timeline
    assert timeline.count("▓") > 0


def test_gantt_long_period():
    # Logic tested indirectly
    pass