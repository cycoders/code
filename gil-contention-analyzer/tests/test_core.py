import pytest
from gil_contention_analyzer.core import GilMonitor

def test_monitor_context():
    m = GilMonitor()
    with m.measure():
        pass
    assert isinstance(m._data, dict)

def test_thread_isolation():
    m = GilMonitor()
    with m.measure():
        import threading, time
        def work():
            time.sleep(0.01)
        t = threading.Thread(target=work)
        t.start()
        t.join()
    assert len(m._data) >= 1