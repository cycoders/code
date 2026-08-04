import sys
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Callable, Dict, List

class GilMonitor:
    def __init__(self) -> None:
        self._data: Dict[int, List[float]] = defaultdict(list)
        self._active = False

    def _profile(self, frame: Any, event: str, arg: Any) -> Callable[[Any, str, Any], Any] | None:
        if event == "call" and self._active:
            thread_id = threading.get_ident()
            start = time.perf_counter()
            # simulate GIL acquisition measurement
            self._data[thread_id].append(start)
        return self._profile

    @contextmanager
    def measure(self):
        self._active = True
        old = sys.getprofile()
        sys.setprofile(self._profile)
        try:
            yield self
        finally:
            sys.setprofile(old)
            self._active = False

import threading  # noqa: E402