import threading
from gil_contention_analyzer.core import GilMonitor

def test_no_threads():
    m = GilMonitor()
    with m.measure():
        pass
    assert len(m._data) == 0