import threading
from .wrappers import _ContendedLock

_original_lock = threading.Lock
_original_rlock = threading.RLock

def install():
    def make_lock(*a, **k):
        return _ContendedLock(_original_lock(*a, **k), "<Lock>")
    threading.Lock = make_lock
    # similar for RLock, Condition, Semaphore...