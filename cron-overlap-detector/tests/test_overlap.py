from datetime import datetime
from cron_overlap_detector.overlap import Interval, find_overlaps

def test_basic_overlap():
    now = datetime(2025, 1, 1, 0, 0)
    a = Interval(now, now.replace(minute=5), 'job1')
    b = Interval(now.replace(minute=3), now.replace(minute=8), 'job2')
    assert len(find_overlaps([a, b])) == 1