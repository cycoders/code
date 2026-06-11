from datetime import datetime, timedelta
from cron_overlap_detector.overlap import Interval, find_overlaps

def test_no_overlap():
    now = datetime(2025, 1, 1)
    a = Interval(now, now + timedelta(minutes=2), 'a')
    b = Interval(now + timedelta(minutes=10), now + timedelta(minutes=12), 'b')
    assert find_overlaps([a, b]) == []