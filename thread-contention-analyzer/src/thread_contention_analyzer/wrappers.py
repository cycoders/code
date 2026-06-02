import time
from threading import Lock, RLock, Condition, Semaphore, BoundedSemaphore

_contention = {}

class _ContendedLock:
    def __init__(self, lock, site):
        self._lock = lock
        self._site = site
    def acquire(self, blocking=True, timeout=-1):
        start = time.perf_counter()
        acquired = self._lock.acquire(blocking, timeout)
        if acquired:
            wait = time.perf_counter() - start
            _contention[self._site] = _contention.get(self._site, (0, 0))
            c, w = _contention[self._site]
            _contention[self._site] = (c + 1, w + wait)
        return acquired
    def release(self):
        self._lock.release()
    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()