import builtins
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from startup_profiler import profiler  # noqa

import sysconfig


class ImportProfiler:
    def __init__(self) -> None:
        self.timings: Dict[str, Dict[str, Any]] = {}
        self._original_import = builtins.__import__
        self._import_stack: List[str] = []
        self.stdlib_path = sysconfig.get_path("stdlib")

    def monkeypatched_import(self):
        """Return monkeypatched __import__."""
        def inner(name: str, globals_: Any = None, locals_: Any = None, fromlist: List = (), level: int = 0) -> Any:
            if self._should_skip(name):
                return self._original_import(name, globals_, locals_, fromlist, level)
            self._import_stack.append(name)
            start = time.perf_counter()
            try:
                mod = self._original_import(name, globals_, locals_, fromlist, level)
            finally:
                dt = time.perf_counter() - start
                self._import_stack.pop()
                self._record_timing(name, dt, mod)
            return mod
        return inner

    def _should_skip(self, name: str) -> bool:
        skips = (
            name.startswith("startup_profiler"),
            name in sys.builtin_module_names,
            name.startswith("encodings."),
            name == "__future__",
            name.startswith("_frozen_importlib"),
        )
        return any(skips)

    def _record_timing(self, name: str, dt: float, mod: Any) -> None:
        if name not in self.timings:
            self.timings[name] = {
                "total": 0.0,
                "self": 0.0,
                "children_time": 0.0,
                "children": [],
                "parent": None,
                "size": 0.0,
                "is_stdlib": False,
            }
        t = self.timings[name]
        t["total"] += dt
        t["self"] = t["total"] - t["children_time"]

        parent_name = self._import_stack[-1] if self._import_stack else None
        if parent_name and parent_name in self.timings:
            self.timings[parent_name]["children"].append(name)
            self.timings[parent_name]["children_time"] += dt
            t["parent"] = parent_name

        # size
        if hasattr(mod, "__file__"):
            fpath = Path(mod.__file__)
            try:
                t["size"] = os.path.getsize(fpath) / 1024  # KB
            except OSError:
                t["size"] = 0.0
            t["is_stdlib"] = str(fpath).startswith(self.stdlib_path)
        else:
            t["is_stdlib"] = name in sys.builtin_module_names

    def get_timings(self) -> Dict[str, Any]:
        timings = {k: dict(v) for k, v in self.timings.items()}
        roots = [k for k in timings if timings[k].get("parent") is None]
        total_time = sum(t["total"] for t in timings.values())
        timings["_meta"] = {"roots": roots, "total_time": total_time}
        return timings
