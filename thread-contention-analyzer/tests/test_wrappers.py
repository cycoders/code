import time
from thread_contention_analyzer.wrappers import _ContendedLock, _contention

def test_contention_tracking():
    lock = _ContendedLock(__import__('threading').Lock(), 'test:1')
    lock.acquire()
    time.sleep(0.01)
    lock.release()
    assert 'test:1' in _contention