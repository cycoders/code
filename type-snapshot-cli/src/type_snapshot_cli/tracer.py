import sys
import types
from pathlib import Path
from typing import Any, Dict
from .aggregator import TypeAggregator
from .emitter import emit_patch

class SnapshotTracer:
    def __init__(self, root: Path):
        self.root = root
        self.agg = TypeAggregator()

    def __call__(self, frame, event, arg):
        if event != "call":
            return
        func = frame.f_globals.get(frame.f_code.co_name)
        if isinstance(func, types.FunctionType) and str(frame.f_code.co_filename).startswith(str(self.root)):
            self.agg.observe(func, frame.f_locals)
        return self

    def finish(self, out: str):
        hints = self.agg.reduce()
        emit_patch(hints, Path(out))

def run_snapshot(target: str, out: str):
    root = Path(target).resolve()
    tracer = SnapshotTracer(root)
    sys.setprofile(tracer)
    try:
        # In real usage the test runner is invoked here
        pass
    finally:
        sys.setprofile(None)
        tracer.finish(out)